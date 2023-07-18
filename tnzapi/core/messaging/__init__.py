""" Reference to tnzapi.base.get.keypad.Keypad """
def Keypad(**kwargs):

    from tnzapi.core.messaging.keypad import Keypad as keypad

    return keypad(**kwargs)