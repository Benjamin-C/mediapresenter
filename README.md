# mediapresenter
Ben's Media Presenter to present media on a second screen using MPV

Plays media on a second screen while keeping all controls on the primary screen.
Has the ability to queue files then play them when the previous file is done or when you tell it to.

Hosts a webserver on port 5000 of all interfaces that gives basic controls

#### To Install:
`$ python -m venv .venv`
`$ source .venv/bin/activate`
`$ pip install -r requirements.txt`

#### To Run:
Make sure `mediapresenter.py` and `.venv/` are in your working directory, then

`$ python mediapresenter.py`

## API reference
## `/pause`
Toggles play/pause of the video.
Returns True/False based on paused state after the action

## `/stop`
Stops the video
Returns the stopped status of the player

## `/seek<dir>`
Seeks `forward`, `back`, or to the `start`
Returns "OK"

## `/next`
Loads the next video.
Returns "OK"

## `/duration`
Gets the length of the clip

## `/time`
Gets the playhead position in the clip

## `/status`
Gets a JSON encoded block of status information
