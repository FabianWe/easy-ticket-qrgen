#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2019 Fabian Wenzelmann
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provides methods to create tickets from a template and create QR codes for them.

Here's a short example on how to generate a ticket token and the qr code for it.

Example:
    >>> token = create_ticket_token()
    >>> qr = create_qr(token)

See the method documentation for more parameters.

After a qr code is generated you can place it on a template image. In the following example the image template is
assumed to be in the file "~/Pictures/ticket_template.png" and the QR code is placed on position (95, 109).

Example:
    >>> # load image
    >>> template_img = Image.open('~/Pictures/ticket_template.png')
    >>> # create a template object
    >>> ticket_template = TicketTemplate(template_img)
    >>> # need to call only once: always place qr code on that position
    >>> ticket_template.add_qr_code((95, 109))
    >>> # render qr code to PIL image
    >>> content = render_pil(qr)
    >>> # place this qr code on the ticket
    >>> ticket = ticket_template.render({'qr_code': content})
    >>> # the same template can be used to render more codes on the ticket
    >>> ticket.show()
"""

import secrets
import string
import pyqrcode
from PIL import Image, ImageDraw
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


def secret_sequence(num, sequence):
    """Creates a random sequence (cryptographically strong random sequence).

    Randomly chooses num elements from sequence and returns the random sequence as a string.

    Args:
        num (int): The length of the output sequence.
        sequence (str): The elements to choose from as a string, each char one possible option.

    Returns:
        str: The random sequence as a string (num random elements from sequence combined).
    """
    return ''.join(secrets.choice(sequence) for _ in range(num))

_int_sequence = string.digits
_qr_alphanumeric_sequence = ''.join(pyqrcode.tables.ascii_codes.keys())


def create_ticket_token(length=64, mode='alphanumeric'):
    """Creates a token for a ticket.

    The output is a cryptographically strong random sequence.

    Args:
        length (int): The length of the token (number of characters).
        mode (str): Either 'int' for a sequence of integer values or 'alphanumeric' for valid QR code chars.

    Returns:
        str: The string representation of the generated token with the given length.
    """
    if mode == 'int':
        return secret_sequence(length, _int_sequence)
    if mode == 'alphanumeric':
        return secret_sequence(length, _qr_alphanumeric_sequence)


def create_qr(token, error='M', **kwargs):
    """Generates a QR code for a given token.

    The token can be generated with create_ticket_token, a QR code instance from pyqrcode is returned.

    Args:
        token (str): The token to encode in the QR code.
        error (str): The error level of the QR code ('L', 'M', 'Q', 'H'), 'L' allowst the least number of errors,
            'H' the most.
        **kwargs (dict): All additional arguments passed to pyqrcode.create.

    Returns:
        pyqrcode.QRCode: The QR code of the token.
    """
    qr = pyqrcode.create(token, error=error, **kwargs)
    return qr


def compute_qr_size(qr, scale, quiet_zone):
    """Compute the size of the QR code when rendered to a PIL image in pixels.

    Because QR codes are squares this is the width and height of the image.

    Args:
        qr (pyqrcode.QRCode): The QR code to compute the size of.
        scale (int): The size in pixels of on module of the QR code (one block in the code).
        quiet_zone (int): The size of blocks left blank in the generated image, that is quiet_zone=4 leaves 4*scale free
            space on each side of the image.

    Returns:
        int: The size of the generated image in pixels.
    """
    version_size = pyqrcode.tables.version_size[qr.version]
    return (scale * version_size) + (2 * quiet_zone * scale)


def render_pil(qr, module_color='black', bg='white', scale=4, quiet_zone=4):
    """Render a QR code as a PIL image.

    The qr code can obtained with create_qr, this QR code is then rendered to a new PIL image.

    Args:
        qr (pyqrcode.QRCode): The QR code to render.
        module_color (PIL color): The color to use for the modules ('blocks') in the QR code.
        bg (PIL color): The background color of the QR code.
        scale (int): The size in pixels of on module of the QR code (one block in the code).
        quiet_zone (int): The size of blocks left blank in the generated image, that is quiet_zone=4 leaves 4*scale free
            space on each side of the image.

    Returns:
        PIL.Image.Image: The QR code rendered to a PIL image.
    """
    code = qr.code
    size = compute_qr_size(qr, scale, quiet_zone)
    img = Image.new('RGB', (size, size), bg)
    d = ImageDraw.Draw(img)
    # iterate over each row
    start_pos = quiet_zone * scale
    y_pos = start_pos
    for row in code:
        x_pos = start_pos
        for entry in row:
            if entry:
                # draw rectangle
                d.rectangle([x_pos,y_pos, x_pos + scale, y_pos + scale], fill=module_color)
            # increase x_pos
            x_pos += scale
        # increase y_pos
        y_pos += scale
    return img


# TODO use image or imagedraw instance?
class Placeable(ABC):
    """An abstract base class for all objects that add something to a template image.

    Each implementation places something on the template image, another image or text with its place method.
    """
    @abstractmethod
    def place(self, image, content):
        """Place something on the template image.

        The type of content depends on the implementation, this can be another image or a text.

        Args:
            image (PIL.Image.Image): The ticket template to be filled with content.
            content: The type depends on the implementation, could be a string or another image.

        Returns:
            None: Changes the image in-place.
        """
        pass


class ImagePlaceable(Placeable):
    """An implementation of Placeable that pastes another image into the template.

    In this case the content argument of place must be a PIL.Image.Image.

    Attributes:
        corner (two element tuple of ints): The point on which the other image is placed in the template in the form
            (x, y).
        scale_to (two element tuple of ints or None): If given the image pasted onto the template gets scaled to
            this dimension (width, height), otherwise the image is not scaled.
    """
    def __init__(self, corner, scale_to=None):
        super().__init__()
        self.corner = corner
        if isinstance(scale_to, int):
            self.scale_to = (scale_to, scale_to)
        else:
            self.scale_to = scale_to

    def place(self, image, content):
        assert isinstance(content, Image.Image)
        if self.scale_to is not None:
            # thumbnail works in-place
            content = content.copy()
            content.thumbnail(self.scale_to)

        image.paste(content, self.corner)


class TicketTemplate(object):
    """Class that represents a ticket template.

    It consists of a template image that is filled with content by Placeable objects.

     Attributes:
         img (PIL.Image.Image): The ticket template as a PIL image.
         placables (dict string to Placeable): Maps names for placables to a concrete Placable implementation.
    """
    def __init__(self, img, placables=None):
        self.img = img
        if placables is None:
            placables = dict()
        self.placables = placables

    def add_qr_code(self, corner, scale_to=None):
        """Add an entry to the placables dictionary with name 'qr_code' that places a generated qr code to the template.

        It simply creates an ImagePlaceable with the specified arguments.

        Args:
            corner (two element tuple of ints): The point on which the QR code is placed in the template in the form
                (x, y).
        scale_to (two element tuple of ints or None): If given the QR code pasted onto the template gets scaled to
            this dimension (width, height), otherwise the image is not scaled. The QR code should not be scaled but
            should be created with the right size before.
        """
        self.placables['qr_code'] = ImagePlaceable(corner, scale_to)

    def render(self, contents):
        """Applies all placables on the given template image.

        contents is a dictionary mapping the names from placables to the actual content.
        For example the placable added by add_qr_code has the name 'qr_code' and thus in content there should be an
        entry 'qr_code' mapping to a PIL image of the QR code.

        Only the placables with a key in contents will be activated.

        Args:
            contents (dict): Mapping the names from placables to the actual content.

        Returns:
            PIL.Image.Image: The template when all objects in placables haven been applied (creates a copy)s.
        """
        # methods work in-place, so we need to make a copy
        img = self.img.copy()
        for key, content in contents.items():
            if key not in self.placables:
                logger.warning('Key of content not found in ticket template: %s', key)
            else:
                self.placables[key].place(img, content)
        return img
