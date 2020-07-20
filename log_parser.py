import os
import os.path
from pathlib import Path

dir_name = "log"
filter_unknown = True


def get_all_filepaths():
    paths = reversed(sorted(Path(dir_name).iterdir(), key=os.path.getmtime))
    output = []
    for path in paths:
        path = path.__str__()
        if "tty" not in path:
            output.append(path)
    return output


def split_file(filename):
    print(filename)
    file = open(filename, "r", encoding="latin-1")
    file_content = file.read()
    file.close()

    file_parts = file_content.split("login attempt ")
    return file_parts


def filter_file_parts(file_parts):
    successful_logins = []
    for file_part in file_parts:
        file_part_parts = file_part.split(" ")

        if file_part_parts[0] == "[root/123456]":
            successful_logins.append(file_part)

    return successful_logins


def get_ip(successful_login):
    login_parts = successful_login.split("HoneyPotTransport,")
    ip_part = login_parts[1]
    split2 = ip_part.split(",")
    ip_part2 = split2[1]
    ip_p = ip_part2.split("]")[0]
    return ip_p


def filter_unknown_channels(successful_logins):
    interesting_logins = []
    for login in successful_logins:
        if "Failure: twisted.conch.error.ConchError: (3, 'unknown channel')" not in login:
            interesting_logins.append(login)

    return interesting_logins


def filter_commands(interestning_logins):
    output = []
    for login in interestning_logins:
        if "executing command" in login:
            output.append(login)
    return output


if __name__ == '__main__':
    output_file = open("output.txt", "w")
    all_ips = {}
    file_paths = get_all_filepaths()
    for file in file_paths:
        output_file.write("\n\n--------------------------------\n" + file + "\n--------------------------------\n\n")
        file_output = filter_file_parts(split_file(file))
        if filter_unknown:
            file_output = filter_commands(filter_unknown_channels(file_output))
        for successlogin in file_output:
            ip = get_ip(successlogin)
            if ip not in all_ips:
                all_ips[ip] = 1
            else:
                all_ips[ip] += 1
            output_file.write(successlogin + "\n\n-----------------------------------------------------------\n\n")

    output_file.close()
    all_ips = {k: v for k, v in reversed(sorted(all_ips.items(), key=lambda item: item[1]))}
    ips_file = open("ips.txt", "w")
    print(all_ips)
    for ip in all_ips:
        ip_str = ip + ": "
        while len(list(ip_str)) < 20:
            ip_str += " "
        ip_str += str(all_ips[ip]) + "\n"
        ips_file.write(ip_str)
    ips_file.close()
