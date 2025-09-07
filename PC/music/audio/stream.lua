-- PC/music/audio/stream.lua
local dfpwm = require("cc.audio.dfpwm")

local Stream = {}
Stream.__index = Stream

local function bytesToPCM(str)
  local out = {}
  local len = #str
  for i = 1, len do
    local b = string.byte(str, i)
    if b >= 128 then b = b - 256 end
    out[i] = b
  end
  return out
end

function Stream.new(sessionId, speaker, client, videoId, totalChunks, format)
  local self = setmetatable({}, Stream)
  self.sessionId = sessionId
  self.speaker = speaker
  self.client = client
  self.videoId = videoId
  self.totalChunks = totalChunks
  self.currentChunk = 0
  self.playing = false
  self.format = format or "pcm8"
  self.decoder = (self.format == "dfpwm") and dfpwm.make_decoder() or nil
  self.buffer = {}
  return self
end

function Stream:start()
  self.playing = true
  parallel.waitForAny(function() self:bufferChunks() end, function() self:playAudio() end)
end

function Stream:bufferChunks()
  while self.playing and self.currentChunk < self.totalChunks do
    for i = 0, 2 do
      local idx = self.currentChunk + i
      if idx < self.totalChunks and not self.buffer[idx] then
        local data = self.client:getChunk(self.videoId, idx)
        if data then self.buffer[idx] = data end
      end
    end
    sleep(0.05)
  end
end

function Stream:playAudio()
  while self.playing and self.currentChunk < self.totalChunks do
    local raw = self.buffer[self.currentChunk]
    if raw then
      local samples
      if self.format == "dfpwm" then
        samples = self.decoder(raw)
      else
        samples = bytesToPCM(raw)
      end

      while not self.speaker.playAudio(samples) do
        if not self.playing then return end
        os.pullEvent("speaker_audio_empty")
      end

      self.buffer[self.currentChunk] = nil
      self.currentChunk = self.currentChunk + 1
    else
      sleep(0.02)
    end
  end
  self.playing = false
end

function Stream:stop() self.playing = false end

return Stream