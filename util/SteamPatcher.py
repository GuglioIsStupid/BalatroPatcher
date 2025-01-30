# libs to get Balatro install path from steam
import os, sys, shutil
import json
import winreg
import zipfile

gameID: str = "2379780"

luaAdditionStart = """
-- call love function that loads file from save folder first
local oldLoad = love.filesystem.load
love.filesystem.load = function(path)
    if love.filesystem.getInfo("Patched/" .. path) then
        print("Loading patched file: " .. path)
		return oldLoad("Patched/" .. path)
	end
    
    if love.filesystem.getInfo(path) then
        return oldLoad(path)
    end

    return nil
end

local oldRequire = require

function require(path)
    if love.filesystem.getInfo("Patched/" .. path .. ".lua") then
        print("Loading patched file: " .. path)
        return oldLoad("Patched/" .. path .. ".lua")()
    end

    return oldRequire(path)
end

lovely = require("smods.lovely")

"""

luaAdditionEnd = """
local function loadMods()
    require("smods.src.core")

    if not love.filesystem.getInfo("Mods") then
        love.filesystem.createDirectory("Mods")
    end
end

loadMods()
"""

def Patch():
    # get steam install path for Balatro
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steamPath = winreg.QueryValueEx(key, "SteamPath")[0]
        winreg.CloseKey(key)
    except:
        print("Steam not found in registry")
        return
    
    print("Steam found at: " + steamPath)

    # get Balatro install path from registry
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App " + gameID)
        balatroPath = winreg.QueryValueEx(key, "InstallLocation")[0]
        winreg.CloseKey(key)
    except:
        print("Balatro not found in registry")
        return
    
    print("Balatro found in registry at: " + balatroPath)

    # extract Balatro.exe
    try:
        # create folder "lua" and extract Balatro.exe
        os.makedirs(balatroPath + "\\lua", exist_ok=True)
        with zipfile.ZipFile(balatroPath + "\\Balatro.exe", 'r') as zip_ref:
            zip_ref.extractall(balatroPath + "\\lua")
    except:
        print("Failed to extract Balatro.exe")
        return
    
    mainLuaPath = balatroPath + "\\lua\\main.lua"
    # read main.lua
    try:
        with open(mainLuaPath, 'r') as file:
            mainLua = file.read()
    except:
        print("Failed to read main.lua")
        return
    
    mainLua = luaAdditionStart + mainLua + luaAdditionEnd

    # write main.lua
    try:
        with open(mainLuaPath, 'w') as file:
            file.write(mainLua)
    except:
        print("Failed to write main.lua")
        return
    
    # copy smods/ folder to lua folder
    try:
        shutil.copytree("smods", balatroPath + "\\lua\\smods")
    except:
        print("Failed to copy smods/ folder")
        return
    
    # zip lua folder to Balatro.love
    try:
        with zipfile.ZipFile(balatroPath + "\\Balatro.love", 'w') as zip_ref:
            for root, dirs, files in os.walk(balatroPath + "\\lua"):
                for file in files:
                    zip_ref.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(balatroPath, "lua")))
    except:
        print("Failed to zip lua folder")
        return