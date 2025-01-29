import util.SteamPatcher as SteamPatcher
import util.APKPatcher as ApkPatcher
import util.PathPatcher as PathPatcher
import sys, os

def main(argv):
    if len(argv) < 2:
        print("Usage: python main.py <patchType (steam|apk)>")
        return
    
    patchType = argv[1].lower()

    if patchType == "steam":
        SteamPatcher.Patch()
    elif patchType == "apk":
        if len(argv) < 3:
            print("Usage: python main.py apk <apkPath>")
            return
        
        apkPath = argv[2]
    else:
        if len(argv) < 3:
            print("Usage: python main.py path <balatroPath>")
            return

        balatroPath = argv[2]
        PathPatcher.Patch(balatroPath)

if __name__ == "__main__":
    main(sys.argv)