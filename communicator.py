import asyncio
import sys

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

class Communicator:
    UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
    UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
    UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

    def __init__(self, debug = False):
        self._tx_queue = asyncio.Queue()
        self._rx_queue = asyncio.Queue()
        self._debug = debug
        self._loop = None

    async def _handle_rx(self, _: BleakGATTCharacteristic, data: bytearray):
        rx = data.decode("ascii").strip()
        if self._debug:
            print("Receive: ", rx)
        await self._rx_queue.put(rx)

    async def _handle_disconnect(self, _: BleakClient):
        print("Device was disconnected")
        for task in asyncio.all_tasks(self._loop):
            task.cancel()

    async def run(self):
        self._loop = asyncio.get_running_loop()
        self._device = await BleakScanner.find_device_by_name("Square Off")

        if self._device is None:
            print("Device not found")
            sys.exit(1)

        print("Found device, connecting...")

        async with BleakClient(self._device, disconnected_callback=self._handle_disconnect) as client:
            await client.start_notify(Communicator.UART_TX_CHAR_UUID, self._handle_rx)
            print("Connected")

            nus = client.services.get_service(Communicator.UART_SERVICE_UUID)
            rx_char = nus.get_characteristic(Communicator.UART_RX_CHAR_UUID)

            while True:
                tx: bytes = await self._tx_queue.get()
                if self._debug:
                    print("Transmit: ", tx)
                await client.write_gatt_char(rx_char, tx)

    def transmit(self, tx: str):
        if self._loop is None:
            return
        txb = tx.strip().encode("ascii")

        assert(len(txb) <= 16) # max packet size
        packet = b'x' + txb + b'z'

        asyncio.run_coroutine_threadsafe(self._tx_queue.put(packet), self._loop).result()

    def receive(self) -> str:
        while self._loop is None:
            pass
        return asyncio.run_coroutine_threadsafe(self._rx_queue.get(), self._loop).result()

def _main():
    """
    Example communication using standard input/output
    """
    import threading

    com = Communicator()

    def stdin():
        while True:
            com.transmit(sys.stdin.readline())

    def stdout():
        while True:
            print(com.receive())

    threading.Thread(target = stdin, daemon = True).start()
    threading.Thread(target = stdout, daemon = True).start()

    asyncio.run(com.run())

if __name__ == "__main__":
    _main()
