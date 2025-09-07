-- PC/music/api/client.lua
local Client = {}
Client.__index = Client

function Client.new(serverUrl)
  return setmetatable({ serverUrl = serverUrl, sessionId = nil }, Client)
end

local function post_json(url, body)
  local headers = { ["Content-Type"] = "application/json", ["User-Agent"] = "CC-Tweaked" }
  local h, err, herr = http.post(url, body, headers)
  if h then return h end

  -- Fallback: table-form (reliable in CC)
  http.request{ url = url, method = "POST", headers = headers, body = body }
  while true do
    local ev, u, handle = os.pullEvent()
    if (ev == "http_success" or ev == "http_failure") and u == url then
      if ev == "http_failure" then if handle then handle.close() end return nil, "http_failure" end
      return handle
    end
  end
end

function Client:createSession()
  local h = post_json(self.serverUrl .. "/session", "{}")
  if not h then return false end
  local txt = h.readAll(); h.close()
  local data = textutils.unserializeJSON(txt)
  if data and data.sessionId then self.sessionId = data.sessionId return true end
  return false
end

function Client:requestTrack(videoId, opts)
  if not self.sessionId then return nil end
  opts = opts or {}
  local payload = textutils.serializeJSON({
    sessionId = self.sessionId,
    videoId = videoId,
    format = opts.format or "pcm8",   -- "pcm8" or "dfpwm"
    sampleRate = opts.sampleRate or 48000,
    duration = opts.duration          -- optional (server default 10)
  })
  local h = post_json(self.serverUrl .. "/track", payload)
  if not h then return nil end
  local txt = h.readAll(); h.close()
  return textutils.unserializeJSON(txt)
end

function Client:getMetadata(videoId)
  local h = http.get(self.serverUrl .. "/metadata/" .. videoId)
  if not h then return nil end
  local txt = h.readAll(); h.close()
  return textutils.unserializeJSON(txt)
end

function Client:getChunk(videoId, chunkId)
  local h = http.get(string.format("%s/chunk/%s/%d", self.serverUrl, videoId, chunkId), nil, true)
  if not h then return nil end
  local data = h.readAll(); h.close()
  return data
end

return Client