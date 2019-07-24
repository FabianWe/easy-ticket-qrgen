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

import secrets
import string
import pyqrcode
from PIL import Image, ImageDraw

def secret_sequence(num, sequence):
    return ''.join(secrets.choice(sequence) for _ in range(num))

_int_sequence = string.digits
_qr_alphanumeric_sequence = ''.join(pyqrcode.tables.ascii_codes.keys())


def create_online_id(length=64, mode='alphanumeric'):
    if mode == 'int':
        return secret_sequence(length, _int_sequence)
    if mode == 'alphanumeric':
        return secret_sequence(length, _qr_alphanumeric_sequence)


def create_qr(key, error='M', **kwargs):
    qr = pyqrcode.create(key, error=error, **kwargs)
    return qr


def render_pil(qr, module_color='black', bg='white', scale=4, quiet_zone=4):
    code = qr.code
    version_size = pyqrcode.tables.version_size[qr.version]
    size = (scale * version_size) + (2 * quiet_zone * scale)
    img = Image.new('RGB', (size, size), bg)
    d = ImageDraw.Draw(img)
    # iterate over each row
    start_pos = quiet_zone * scale
    y_pos = start_pos
    #d.rectangle([0, 0, size, size], fill='black')
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
    img.show()
    return img

#key = create_online_id()
#print(key)
#qr = create_qr(key)
#render_pil(qr, scale=6, quiet_zone=0)