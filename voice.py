from typing import Iterable
import pocketsphinx as ps
import sounddevice

SAMPLE_RATE = 16000

class VoiceControl:

    TRANSLATIONS = {
        # Pieces
        "pawn"    : "p",
        "knight"  : "n",
        "bishop"  : "b",
        "rook"    : "r",
        "queen"   : "q",
        "king"    : "k",

        # Squares
        "alpha"   : "a",
        "bravo"   : "b",
        "charlie" : "c",
        "delta"   : "d",
        "echo"    : "e",
        "foxtrot" : "f",
        "golf"    : "g",
        "hotel"   : "h",

        "one"     : "1",
        "two"     : "2",
        "three"   : "3",
        "four"    : "4",
        "five"    : "5",
        "six"     : "6",
        "seven"   : "7",
        "eight"   : "8",

        # Other
        "take"    : "x",
        "capture" : "x",
        "promote" : "=",
    }

    def __init__(self):
        self._decoder = ps.Decoder(ps.Config(), samplerate=SAMPLE_RATE)
        self._decoder.add_jsgf_file("move", "move.jsgf")
        self._decoder.activate_search("move")

        self._endpoint = ps.Endpointer(sample_rate = SAMPLE_RATE)
        self._buffer_size = self._endpoint.frame_bytes

        self._stream = sounddevice.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=self._buffer_size // 2,
            dtype="int16",
            channels=1,
        )

    def listen(self) -> Iterable[str]:
        self._stream.start()
        print("Listening for voice move input")

        try:
            run = True
            while run:
                buf, _ = self._stream.read(self._buffer_size // 2)
                prev_in_speech = self._endpoint.in_speech

                if len(buf) == self._buffer_size:
                    speech = self._endpoint.process(buf)
                else:
                    speech = self._endpoint.end_stream(buf)
                    run = False

                if speech is not None:
                    if not prev_in_speech:
                        print("Speech started at {:.2f}".format(self._endpoint.speech_start))
                        self._decoder.start_utt()

                    self._decoder.process_raw(speech)

                    if not self._endpoint.in_speech:
                        print("Speech ended at {:.2f}".format(self._endpoint.speech_end))
                        self._decoder.end_utt()
                        if hyp := self._decoder.hyp():
                            print(f"Score = {hyp.score:.3f}, Prob = {hyp.prob:.3f}, Phrase = {hyp.hypstr}")
                            yield hyp.hypstr
        finally:
            self._stream.stop()

    @classmethod
    def translate_phrase(cls, phrase: str) -> str:
        return "".join((cls.TRANSLATIONS[word] for word in phrase.split()))

if __name__ == "__main__":
    for phrase in VoiceControl().listen():
        print(phrase)
        print(VoiceControl.translate_phrase(phrase))
