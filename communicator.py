import asyncio
import threading
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

    def _handle_disconnect(self, _: BleakClient):
        print("Device was disconnected")
        for task in asyncio.all_tasks(self._loop):
            task.cancel()

    async def _run(self):
        self._loop = asyncio.get_running_loop()

        print("Searching for device...")
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
                tx: bytes|None = await self._tx_queue.get()
                if tx is None:
                    return
                if self._debug:
                    print("Transmit: ", tx)
                await client.write_gatt_char(rx_char, tx)
                await asyncio.sleep(0.1)

    def run(self):
        def target():
            try:
                asyncio.run(self._run())
            except asyncio.exceptions.CancelledError:
                pass

        threading.Thread(target=target).start()

    def stop(self):
        print("Disconnecting...")
        asyncio.run_coroutine_threadsafe(self._tx_queue.put(None), self._loop).result()

    def transmit(self, tx: str):
        while self._loop is None:
            pass

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
    com.run()

    def stdin():
        while True:
            com.transmit(sys.stdin.readline())

    def stdout():
        while True:
            print(com.receive())

    threading.Thread(target = stdin, daemon = True).start()
    threading.Thread(target = stdout, daemon = True).start()

if __name__ == "__main__":
    _main()
