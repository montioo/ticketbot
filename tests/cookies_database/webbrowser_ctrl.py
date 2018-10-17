import time
import subprocess
import webbrowser


def browser_process():
    # Laeuft nicht, ist mir auch egal
    p = subprocess.Popen(["firefox", "http://www.google.com"])
    time.sleep(10) #delay of 10 seconds
    p.kill()


def check_browser_available(browser_name):
    try:
        ff = webbrowser.get(browser_name)
        return True
    except webbrowser.Error:
        return False


def main():
    print(check_browser_available('grail'))
    print(check_browser_available('firefox'))


if __name__ == "__main__":
    main()
