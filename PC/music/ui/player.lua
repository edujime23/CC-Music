-- PC/music/ui/player.lua
local Player = {}
Player.__index = Player

function Player.new(termObj)
  local self = setmetatable({}, Player)
  self.term = termObj
  self.width, self.height = termObj.getSize()
  self.currentTrack = nil
  self.progress = 0
  self.isPlaying = false
  return self
end

function Player:draw()
  self.term.setBackgroundColor(colors.black)
  self.term.clear()
  self:drawTitleBar()

  if self.currentTrack then
    self:drawAlbumArt()
    self:drawTrackInfo()
    self:drawProgressBar()
  else
    self:drawWelcomeScreen()
  end

  self:drawControls()
end

function Player:drawTitleBar()
  self.term.setBackgroundColor(colors.lightBlue)
  self.term.setTextColor(colors.white)
  self.term.setCursorPos(1, 1)
  local title = " CC-Music Player "
  local padding = string.rep(" ", self.width - #title)
  self.term.write(title .. padding)
end

function Player:drawAlbumArt()
  if not self.currentTrack or not self.currentTrack.thumbnail then return end

  local lines = {}
  for line in self.currentTrack.thumbnail:gmatch("[^\n]+") do table.insert(lines, line) end
  local ox, oy = 2, 3
  for i, line in ipairs(lines) do
    self.term.setCursorPos(ox, oy + i - 1)
    for j = 1, #line do
      local color = tonumber(line:sub(j, j), 16) or 0
      self.term.setBackgroundColor(2 ^ color)
      self.term.write(" ")
    end
  end
end

function Player:drawTrackInfo()
  local t = self.currentTrack
  if not t then return end
  self.term.setBackgroundColor(colors.black)
  self.term.setTextColor(colors.white)
  self.term.setCursorPos(20, 3)
  self.term.write("Title: " .. (t.title or "Unknown"))
  self.term.setCursorPos(20, 4)
  self.term.write("Artist: " .. (t.artist or "Unknown"))
  self.term.setCursorPos(20, 5)
  self.term.write(string.format("Fmt: %s, %dHz", t.format or "pcm8", t.sampleRate or 48000))
  self.term.setCursorPos(20, 6)
  self.term.setTextColor(self.isPlaying and colors.green or colors.red)
  self.term.write(self.isPlaying and "♪ Playing" or "⏸ Stopped")
end

function Player:drawProgressBar()
  local y = self.height - 3
  local barWidth = self.width - 4
  self.term.setBackgroundColor(colors.gray)
  self.term.setCursorPos(3, y)
  self.term.write(string.rep(" ", barWidth))
  local filled = math.floor(barWidth * (self.progress or 0))
  if filled > 0 then
    self.term.setBackgroundColor(colors.green)
    self.term.setCursorPos(3, y)
    self.term.write(string.rep(" ", filled))
  end
end

function Player:drawWelcomeScreen()
  local msg = "Press SPACE to play test track"
  local x = math.floor((self.width - #msg) / 2)
  local y = math.floor(self.height / 2)
  self.term.setBackgroundColor(colors.black)
  self.term.setTextColor(colors.lightGray)
  self.term.setCursorPos(x, y)
  self.term.write(msg)
end

function Player:drawControls()
  self.term.setBackgroundColor(colors.black)
  self.term.setTextColor(colors.lightGray)
  self.term.setCursorPos(2, self.height)
  self.term.write("SPACE: Play/Pause | Q: Quit")
end

return Player