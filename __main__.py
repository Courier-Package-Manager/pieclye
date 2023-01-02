"""
semi-cli that tests typing speed.

TODO:

  HIGH:
  - Finish up cmd line

  MEDIUM:
  - Json save feature to replace text feature
  - 1 save file only
  - adjustable config
  - multiplayer

  LOW:

DONE: 
 - better looking screens
 - consistent err msg format
 - Implement accuracy feature
 - Random text generation
 - Clear screen functionality
 - Cross platform support
 - Fix index errors
"""

# NOTE extra libs
import os
import time
import glob
import math

from difflib import SequenceMatcher

# NOTE server libs
import socket
from _thread import *

# NOTE os / std libs
import sys
import json
import random
import subprocess as sp

# NOTE dynamic vars for start command -> start_text(...)
_exit = 0
races = 0

# Install pygame if not installed already
try:
    import pygame
except ImportError:
    sp.call(['python3', '-m', 'pip', 'install', '-r', 'requirements.txt'])
    _exit += 1
except (SystemError, SyntaxError):
    sys.stdout("This program must be run from python >=3.5")
    _exit += 1
finally:
    if _exit:
        sys.exit(_exit)
    print(f"Initialization errors: {_exit}")

pygame.init()

class Server(socket.socket):
    """ Server for easier integration with game """
    _flags = (socket.AF_INET, socket.SOCK_STREAM)
    _server_ip = socket.gethostbyname(socket.gethostname())
    _port = 5555
    _client_limit = 2
    def __init__(self):
        super().init(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.bind((Server._server_ip, Server._port))
        except socket.error as e:
            str(e)

    def _listen(self):
        self.listen(Server._client_limit)

    def thread_client(self, conn):
        """ Handle receiving of client information / sending client information """
        conn.send(str.encode(f"[{self._client_limit}] Connected to {self._server_ip}*{self._port}"))
        reply = ""
        while 1:
            try:
                client_msg = conn.recv(2048) # args = max amount of bytes allowed from client
                reply = client_msg.decode("utf-8")
                
                if not client_msg:
                    print(f"{conn} disconnected")
                    break;
                else:
                    print(f"Received: {reply}")
                    print(f"Sending: {reply}")

                conn.sendall(string.encode(reply))
            except:
                break

        print("Lost connection")
        conn.close()

    def thread_server(self):
        """ listens for clients """
        conn, addr = self.accept()
        print(f"Connected to: {addr}")

        start_new_thread(self.thread_client, (conn,)) # NOTE start_new_thread from _thread.start_new_thread lib


class Client(socket.socket):
    def __init__(self):
        super().__init__(*Server._flags)
        self.server = Server._server_ip
        self.port = Server._port
        self.addr = (self.server, self.port)
        self.id = self._connect()

    def _connect(self) -> str:
        """ Connect to server and recv information from server """
        try:
            self.connect(self.addr)
            return self.recv(2048).decode()
        except:
            pass

    def _send(self, data):
        try:
            self.send(str.encode(data))
            return self.recv(2048).decode()
        except socket.error as e:
            print(e)

    @property
    def wpm(self):
        return self.id

class Score:
    """ For keeping track of individual scores """
    def __init__(self):
        self.time = time.time() # Time score was set
        self.wpm = wpm # WPM of score
        self.cpm = cpm # CPM of score
        self.tid = tid # text id of score

class Text:
    """ For easier management as oppose to json / dict """
    def __init__(self, _author: str, _year: int, _quote: str, _text: str):
        self.author = _author
        self.year   = _year
        self.quote  = _quote
        self.text   = _text

    @property
    def length(self) -> int:
        """ Get chars in text """
        return len(self.text)

text_list = [
        Text(
            _author="James Burrows",
            _year=2012,
            _quote="They don\'t know that we know they know that we know.",
            _text="Friends",
            ),
        Text(
            _author="Master OOgway",
            _year=2008,
            _quote="Yesterday is history, tomorrow is a mystery, but today is a gift. That is why it\'s called the present.",
            _text="Kung-fu Panda",
            ),
        Text(
            _author="Robert Baden-Powell",
            _year=1908,
            _quote="The quick brown fox jumped over the lazy dog.",
            _text="Scouting for Boys",
            ),
        ]

class Quote:
    scores = []
    def __init__(self):
        """ Quote constructor """
        self.text = random.choice(text_list)
        self.chars = len([i for i in self.text.quote]) # num. of chars (including whitespaces)

    def stdout_text(self) -> None:
        """ Properly print out quote, printinw a new line every 10 words """
        for i, k in enumerate(self.text.quote.split(" ", len(self.text.quote))):
            if i in [i for i in range(10, 100, 10)]:
                print(k, end="\n")
            else:
                print(k, end=" ")

    def get_wpm(self, time) -> float:
        """ Returns average words per minute """
        try:
            result = round(((self.chars / 5) / time*60), 2)
        except ZeroDivisionError:
            clear_screen()
            sys.exit(0)
        return result

    def get_cpm(self, time) -> float:
        """ returns average characters per minute """
        return (self.chars / time) // 0.5

    def get_acc(self, text, _input) -> float:
        """ gets acc by comparing errors from original text """
        return round(SequenceMatcher(None, text, _input).ratio() * 100)

    def get_awpm(self, wpm, acc) -> float:
        """ Adjusted for num of errors """
        awpm = round(wpm * acc)
        if awpm >= wpm:
            return wpm
        else:
            return awpm

running = True

def clear_screen() -> (None, str):
    """ Clears the screen (linux and mac) """
    try:
        sp.run(['clear'])
    except Exception as str_exc:
        return str(str_exc)


def num_scores() -> str:
    """
        Counts the number of score files to prevent overwrite
        This then returns a string / score name.
    """
    id_ = len([i for i in glob.glob("./*.txt")]) + 1
    return f"save-{id_}.txt"

def save_scores() -> None:
    """
        Returns true if save is successful & false if not.
    """
    fname = None
    try:
        fname = num_scores()
        with open(fname, "w") as file:
            for i in Quote.scores:
                file.write(str(i)+'\n')
                file.close()
    except Exception as string_exc:
        print(str(string_exc))
        sys.exit(1)
    finally:
        print(f"Saved to: {os.path.join(os.getcwd(), fname)}")
        return;


def query_save() -> None:
    """ Asks if user would like to save their score """
    _r = None
    try:
        if len(Quote.scores) == 1:
            print(f"Would you like to save your score?")
        elif len(Quote.scores) >= 2:
            print(f"Would you like to save your scores? ({len(Quote.scores)}) texts)")
    finally:
        try:
            while True:
                _r = str(input(" [Y/N] -> ")).upper()
                if _r == "Y":
                    save_scores()
                    return;
                elif _r == "N":
                    return;
                else:
                    continue
        except KeyboardInterrupt:
            print("\nExiting without saving.")
            sys.exit(0)

def offer_retry() -> None:
    """ offers to try again """
    print("Would you like to complete another test?")
    try:
        while True:
            _q = str(input(" [Y/N] -> ")).upper()
            if _q == "Y":
                start_text()
                return;
            elif _q == "N":
                query_save()
                return;
            else:
                continue
    except KeyboardInterrupt:
        print("\nExiting without saving.")
        sys.exit(0)


def start_text(quote=Quote()) -> None:
    """ Initiates test start (including time) """
    clear_screen()
    print("\n\t\t\t\t[press enter to start]\t\t\t\t\n")
    clear_screen()
    quote.stdout_text()
    time_start = time.time()

    wpm = str(input("\n -> ")) # NOTE this starts test
    time_end = time.time()

    clear_screen()
    time_total = round(time_end-time_start)

    # TODO figure out way to format without if statements
    if time_total < 60:
        if time_total < 10:
            print(f"Time: 0:0{time_total}")
        else:
            print(f"Time: 0:{time_total}")
    else:
        print("Time limit exceeded.")
        return;

    # NOTE quote statistics
    rwpm = quote.get_wpm(time_total)
    acc = quote.get_acc(quote.text.quote, wpm)
    awpm = quote.get_awpm(rwpm, acc)

    print("WPM: {WPM}\n ({ACC}% accuracy)".format(WPM=rwpm, ACC=acc))
    print(f"Source - ({quote.text.text}) by {quote.text.author} ")

    Quote.scores.append(quote.get_wpm(time_total))
    del quote
    offer_retry()

def host(addr, port) -> (None, bool):
    """ Host multiplayer server """
    server = socket.socket()

def cat(_file) -> None:
    """ Read contents of file """
    with open(_file, 'r') as fp:
        try:
            contents = fp.read().strip()
            print(contents)
        finally:
            fp.close()
            return;

def reset() -> None:
    """ Reset all save-#.txt files """
    files = []
    for i in glob.glob('./*.txt'):
        if i != './requirements.txt':
            files.append(i)
    if len(files) >= 1:
        print("Files to delete:")
        for i in files:
            print(f"\t{i}")
        print("Are you sure you want to reset all scores?")
        query_response()
    else:
        print("There seems to be no available scores to delete")
        return;

def ls() -> None:
    """ list files in current directory """

    files = []

    for i in glob.glob("./*"):
        files.append(i)

    for i, k in enumerate(files):
        if i == len(files)-1:
            if './' in k:
                print(k.split('./')[1])
            else:
                print(k)
            break;
        else:
            if './' in k:
                print(k.split('./')[1], end="\t")
            else:
                print(k, end="\t")
    return;

def query_response() -> (None, bool):
    """ Ask for permission to deleate files (reset() function related) """
    try:
        confirm = input("[y=yes/n=no] (default=y) >> ")
        query_delete(confirm)
    except KeyboardInterrupt:
        return False;
    finally:
        return;

def query_delete(confirm) -> (None, object):
    """ Ask for permission to deleate files (reset() and query_response() function related) """
    if confirm.startswith("y"):
        try:
            for i in files:
                print(f"Removing {i}")
                os.remove(i)
        except PermissionError:
            print("Error: you do not have valid permissions to complete this operation. Please run program as elevated user.");
            sys.exit(1)
        finally:
            return;
    elif confirm.startswith("n"):
        pass
    else:
        if not query_response():
            print("\nExecution halted by user")
            exit(1)
            sys.exit(1) # FIXME sys.exit(1) nor exit(1) closes program immediately

def proc_command(cmd: str):
    """ processes various commands """
    for i in ['help', '--help', '/?', '-h', '-help', '/help']:
        if cmd.startswith(i):
            if cmd in ['edit']:
                print("""
                usage: edit [-f] ...\n
                    -f, --force         overwrite existing preferences with current configuration.
                    -d, --default       overwrite existing preferences with default configuration.

                commands:
                    edit wrap           toggle quote text wrapping [current=on]
                    edit wpm            toggle wpm summary
                    edit awpm           toggle awpm (accurate words per minute) summary
                    edit cpm            toggle cpm summary
                    edit quoteinfo      toggle info summary at end of quote
                """)
                break; continue;
            else:
                print("""
                Help: prints out this help message

                edit                goto edit ctx menu
                teststart           start test
                cls                 clear screen        alias: clear
                exit                stop program        alias: stop | quit
                reset               reset scores        
                cat [file]          output contents of [file]
                """)
                break; continue;
        else:
            if cmd in ['teststart', 'start']:
                start_text()
                break; continue;
            elif cmd.startswith('reset'):
                reset()
                break; continue;
            elif cmd.startswith('cls'):
                clear_screen()
                break; continue;
            elif cmd.startswith('clear'):
                clear_screen()
                break; continue;
            elif cmd == 'ls': # NOTE including 'or' here will break this.
                ls()
                break; continue;
            elif cmd.startswith('cd'): # NOTE do not set function as 
                                       # verbose error handling is 
                                       # required for `cd` command.
                try:
                    os.chdir(cmd.split(' ')[1])
                    break; continue;
                except IndexError:
                    break; continue;
                except Exception as exc_err:
                    print(str(exc_err))
                    break; continue;
            elif cmd.startswith('cat'):
                try:
                    _file = cmd.split(' ')[1]
                    cat(_file)
                    break; continue;
                except IndexError:
                    print("Please specify a filename")
                    return;
                except FileNotFoundError:
                    print(f"cat: {_file}: No such file or directory")
                    return;
                except IsADirectoryError:
                    print(f"cat: {_file}: Cannot open `{_file}` as it is a directory")
                    return;


def main() -> object:
    """ Primary call function """
    while (running):
        try:
            cmd = input(f"({os.getcwd()}) -> ")
            proc_command(cmd)
        except KeyboardInterrupt:
            print("\nExecution halted by user")
            sys.exit(1)

if __name__ == "__main__": # NOTE required to ensure working directory is valid
    clear_screen()
    main()
else: # FIXME denote with correct error type
    print("Invalid working directory.")
    sys.exit(1)
