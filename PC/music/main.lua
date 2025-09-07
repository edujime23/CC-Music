-- PC/music/main.lua
local Client = require("api.client")
local Player = require("ui.player")
local Stream = require("audio.stream")

local SERVER_URL = "https://cc-music.psnedujime.workers.dev"
local REQUEST_FORMAT = "pcm8"  -- change to "dfpwm" to test DFPWM

local client = Client.new(SERVER_URL)
local speaker = peripheral.find("speaker")
local termObj = term.current()

if not speaker then print("Error: No speaker found!") return end

local playerUI = Player.new(termObj)
local currentStream

local function startTrack(videoId)
  print("Requesting track:", videoId)

  local trackInfo = client:requestTrack(videoId, { format = REQUEST_FORMAT, sampleRate = 48000 })
  if not trackInfo then print("Failed to request track!") return end

  print("Track requested, waiting for processing...")
  while true do
    sleep(1)
    local metadata = client:getMetadata(videoId)
    if metadata and metadata.ready then
      print("Track ready! Starting playback...")
      playerUI.currentTrack = metadata
      playerUI.isPlaying = true

      currentStream = Stream.new(client.sessionId, speaker, client, videoId, metadata.totalChunks, metadata.format or "pcm8")
      currentStream:start()
      break
    end
  end
end

local function main()
  print("CC-Music Player Starting...")
  if not client:createSession() then print("Failed to connect to server!") return end
  print("Connected! Session ID:", client.sessionId)

  while true do
    playerUI:draw()
    local e, p1 = os.pullEvent()
    if e == "key" then
      if p1 == keys.space then
        if currentStream and currentStream.playing then
          currentStream:stop()
          playerUI.isPlaying = false
        else
          startTrack("test123")
        end
      elseif p1 == keys.q then
        if currentStream then currentStream:stop() end
        break
      end
    end
    sleep(0.05)
  end

  term.clear()
  term.setCursorPos(1, 1)
  print("CC-Music Player stopped.")
end

main()