__tile__ = 'easyticket_qrgen'
__version__ = '1.0'

from .qr_ticketgen import secret_sequence, create_ticket_token, create_qr, compute_qr_size, render_pil, Placeable, ImagePlaceable, TicketTemplate