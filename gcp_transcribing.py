from google.cloud import speech_v1
from google.oauth2 import service_account

import json


def transcribe(audio_file, service_account_file):
    """
    Args:
      audio_file string representing the path to the audio files you want to transcribe.
      service_account_file string representing the path to the key file of your gcp service account.
    """
    creds = service_account.Credentials.from_service_account_file(service_account_file)
    client = speech_v1.SpeechClient(credentials=creds)

    # storage_uri = 'gs://cloud-samples-data/speech/brooklyn_bridge.flac'

    # When enabled, the first result returned by the API will include a list
    # of words and the start and end time offsets (timestamps) for those words.
    enable_word_time_offsets = True

    # The language of the supplied audio
    language_code = "en-US"
    config = {
        "encoding": "FLAC",
        "sample_rate_hertz": 44100,
        "enable_word_time_offsets": enable_word_time_offsets,
        "language_code": language_code,
    }
    with open(audio_file, "rb") as file:
        audio = {"content": file.read()}

    response = client.recognize(config, audio)
    # The output will be a list containing 3-tuples (word, start_time, end_time)
    output = list()

    # The result includes start and end time word offsets
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        for word in alternative.words:
            output.append((word.word, to_float_seconds(word.start_time), to_float_seconds(word.end_time)))

    # Return the output list sorted primarily by start_time, secondarily by end_time
    return sorted(output, key=lambda res: (res[1], res[2]))


def write_to_file(data, path):
    """ First serializes, then writes to a file named as the path parameter."""
    serializable = {
        "words": [e[0] for e in data],
        "start_times": [e[1] for e in data],
        "end_times": [e[2] for e in data],
    }
    serialized = json.dumps(serializable)
    with open(path, "w+") as file:
        file.write(serialized)


def to_float_seconds(gcp_timestamp):
    return float(gcp_timestamp.seconds + gcp_timestamp.nanos/10**9)


if __name__ == "__main__":
    python_data = transcribe(
        "./mono.flac",
        "/home/sjoerdvandenbos/Downloads/my_gcp_key.json",
    )
    print(python_data)
    write_to_file(python_data, "gcp_results.json")
