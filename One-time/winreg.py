import winreg

# https://docs.python.org/3/library/winreg.html
# connecting to key in registry
access_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
keyval = r"SOFTWARE\Policies\Microsoft\Windows\OneDrive"
try:
    access_key = winreg.OpenKey(access_registry, keyval, 0, winreg.KEY_ALL_ACCESS)
except:
    access_key = winreg.CreateKey(access_registry, keyval)


print("QueryValueEx - Before: " + str(winreg.QueryValueEx(access_key, "DisableFileSyncNGSC")[0]))

if winreg.QueryValueEx(access_key, "DisableFileSyncNGSC")[0] == 1:
    winreg.SetValueEx(access_key, "DisableFileSyncNGSC", 0, winreg.REG_DWORD, 0)
    print("QueryValueEx - After: " + str(winreg.QueryValueEx(access_key, "DisableFileSyncNGSC")[0]))
winreg.CloseKey(access_key)
#############################################

access_registry1 = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
keyval1 = r"Software\Policies\Mozilla\Firefox"
try:
    access_key1 = winreg.OpenKey(access_registry1, keyval1, 0, winreg.KEY_ALL_ACCESS)
except:
    access_key1 = winreg.CreateKey(access_registry1, keyval1)


print("QueryValueEx - Before: " + str(winreg.QueryValueEx(access_key1, "DisableFirefoxAccounts")[0]))

if winreg.QueryValueEx(access_key1, "DisableFirefoxAccounts")[0] == 1:
    winreg.SetValueEx(access_key1, "DisableFirefoxAccounts", 0, winreg.REG_DWORD, 0)
    print("QueryValueEx - After: " + str(winreg.QueryValueEx(access_key1, "DisableFirefoxAccounts")[0]))
winreg.CloseKey(access_key1)


# accessing the key to open the registry directories under
# access_key1 = winreg.OpenKey(access_registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion")
# for n in range(20):
#     try:
#         x = winreg.EnumKey(access_key, n)
#         print(x)
#     except:
#         break

# print("QueryInfoKey: " + str(winreg.QueryInfoKey(access_key)))

# keyVal = r"Software\Microsoft\Internet Explorer\Main"
# try:
#     key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyVal, 0, winreg.KEY_ALL_ACCESS)
# except:
#     key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, keyVal)
# winreg.SetValueEx(key, "Start Page", 0, winreg.REG_SZ, "https://www.blog.pythonlibrary.org/")
# winreg.CloseKey(key)
