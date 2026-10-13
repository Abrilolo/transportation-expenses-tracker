"""Human-readable labels for the common Suica/PASMO history codes."""

CONSOLE_TYPES = {
    0x03: "Fare adjustment machine",
    0x04: "Portable terminal",
    0x05: "Onboard terminal",
    0x07: "Ticket vending machine",
    0x08: "Ticket vending machine",
    0x09: "Charge machine",
    0x12: "Ticket vending machine",
    0x16: "Automatic ticket gate",
    0x1C: "Transfer fare adjustment machine",
    0xC8: "Vending machine",
}

PROCESS_TYPES = {
    0x01: "Fare payment",
    0x02: "Charge",
    0x0F: "Bus",
    0x46: "Retail purchase",
}

RAIL_PROCESS_CODES = {0x01, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x14}


def console_name(code: int) -> str:
    return CONSOLE_TYPES.get(code, f"Unknown (0x{code:02X})")


def process_name(code: int) -> str:
    return PROCESS_TYPES.get(code, f"Unknown (0x{code:02X})")


def is_rail_process(code: int) -> bool:
    return code in RAIL_PROCESS_CODES
