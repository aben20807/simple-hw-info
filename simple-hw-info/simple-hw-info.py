import subprocess
# import argparse
import time
from types import SimpleNamespace
import platform
import re
import json

this_pc_os = platform.system()

"""terminal color"""
TC = SimpleNamespace(
    **{
        "YELLOW": "\033[33m",
        "GREEN": "\033[92m",
        "RED": "\033[91m",
        "BLUE": "\033[34m",
        "RESET": "\033[0m",
    }
)


class Cmd:
    def __new__(
        self, cmd: str, cwd="./", timeout_duration=None, suppress=True
    ) -> tuple[int, str, str]:
        self.cmd = cmd
        self.cwd = cwd
        self.returncode = 0
        self.has_err = True

        if not suppress:
            print(f"{self.cmd}", end="", flush=True)
        cwd_not_cur = f" in {self.cwd}" if self.cwd != "./" else ""

        """ process setup """
        process = None
        enc = ""
        if this_pc_os == "Windows":
            enc = "cp950"
            process = subprocess.Popen(
                ["powershell", self.cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                # executable="bash",
                cwd=self.cwd,
            )
        elif this_pc_os == "Linux":
            enc = "utf8"
            process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                executable="bash",
                cwd=self.cwd,
            )
        else:
            raise RuntimeError(f"`{platform.system()}` is not supported")

        """ execution """
        out = bytearray()
        err = bytearray()
        timeStarted = time.time()
        try:
            _out, _err = process.communicate()
            out = _out if _out is not None else out
            err = _err if _err is not None else err
            self.returncode = process.returncode
            if process.returncode != 0:
                raise RuntimeError(
                    f"returncode is not 0 but {process.returncode}. "
                    + str(out + err, encoding=enc)
                )
        except:
            if not suppress:
                print(f"{cwd_not_cur} {TC.RED}[failed]{TC.RESET}")
            return self.returncode, str(out, encoding=enc), str(err, encoding=enc)

        timeDelta = time.time() - timeStarted
        if not suppress:
            print(f"{cwd_not_cur} {TC.GREEN}[passed]{TC.RESET} ({timeDelta:.3f}s)")
        self.has_err = False
        return self.returncode, str(out, encoding=enc), str(err, encoding=enc)


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--csv", action="store_true")
    # args = parser.parse_args()

    if this_pc_os == "Windows":
        # Check
        rc, out, err = Cmd("""fastfetch -s cpu --format json""")
        if rc != 0:
            print("Please install fastfetch")
            input("Press enter to quit")
            import sys

            sys.exit(1)
        
        print("simple hw info:")
        print("cpu, cores&threads, gpu, memory, ssd, hdd")
        # CPU
        rc, out, err = Cmd("""fastfetch -s cpu --format json""")
        cpu = json.loads(out)[0]["result"]["cpu"]

        # CPU detail
        rc, out, err = Cmd("""wmic cpu get NumberOfCores,ThreadCount /format:list""")
        cpu_core_cnt = re.search(r"NumberOfCores=(.*?)\r", out).group(1)
        cpu_thread_cnt = re.search(r"ThreadCount=(.*?)\r", out).group(1)

        # GPU
        rc, out, err = Cmd("""fastfetch -s gpu --format json""")
        gpus = json.loads(out)[0]["result"]
        gpu = ""
        for gpu_i in gpus:
            gpu += gpu_i["name"] + "+"
        gpu = gpu[:-1]

        # Memory detail
        rc, out, err = Cmd(
            """wmic memorychip get SMBIOSMemoryType,Capacity /format:list"""
        )
        out = [e for e in [d.strip() for d in out.split("\r\r\n\r\r\n\r\r\n")] if e]
        memory = ""
        memeorys = []
        for dimm in out:
            SMBIOSMemoryType = re.search(
                r"\s*?SMBIOSMemoryType.*?=\s*(.*)\s*", dimm
            ).group(1)
            Capacity = round(
                int(re.search(r"\s*?Capacity.*?=\s*(.*?)\s*\r", dimm).group(1))
                / (1024**3)
            )
            memeorys.append(
                {"SMBIOSMemoryType": hex(int(SMBIOSMemoryType)), "Capacity": Capacity}
            )
            memory += str(Capacity) + "+"
        memory = memory[:-1] + "G"

        memory_type = memeorys[0]["SMBIOSMemoryType"]
        # https://www.dmtf.org/sites/default/files/standards/documents/DSP0134_3.4.0a.pdf - 7.18.2 Memory Device — Type
        try:
            memory_type = {
                "0x18": "DDR3",
                "0x19": "FBD2",
                "0x1A": "DDR4",
                "0x1B": "LPDDR",
                "0x1C": "LPDDR2",
                "0x1D": "LPDDR3",
                "0x1E": "LPDDR4",
                "0x1F": "Logical non-volatile device",
                "0x20": "HBM (High Bandwidth Memory)",
                "0x21": "HBM2 (High Bandwidth Memory Generation 2)",
                "0x22": "DDR5",
                "0x23": "LPDDR5",
            }[memory_type]
        except:
            print(
                f"[ERROR] `{memory_type}` memeory type not found, please update the table"
            )
            memory_type = None
        memory_type = " (" + memory_type + ")" if memory_type is not None else None
        # print(memory_type)

        # Disk
        rc, out, err = Cmd(
            """wmic diskdrive get MediaType,Size,SerialNumber /format:list"""
        )
        out_disks = [d for d in out.split("\r\r\n") if d]
        disks_list = []
        for i in range(0, len(out_disks), 3):
            one_disk = {}
            for j in range(3):
                field, val = out_disks[i + j].split("=")
                one_disk[field] = val.strip()
            disks_list.append(one_disk)

        ssds = ""
        hdds = ""
        for d in disks_list:
            if not d["MediaType"].startswith("External"):
                rc, out, err = Cmd(
                    f"""Get-PhysicalDisk -SerialNumber {d["SerialNumber"]} | select MediaType"""
                )
                ssd_or_hdd = [i.strip() for i in out.split("\r\n") if i][2]
                if ssd_or_hdd == "SSD":
                    ssds += f"{round(int(d['Size']) / 1000_000_000)}G+"
                else:
                    hdds += f"{round(int(d['Size']) / 1000_000_000)}G+"

        ssds = ssds[:-1] if ssds != "" else "-"
        hdds = hdds[:-1] if hdds != "" else "-"

        print(
            f"\"{cpu}, {cpu_core_cnt}C{cpu_thread_cnt}T, {gpu}, {memory}{memory_type if memory_type is not None else ''}, {ssds}, {hdds}\""
        )
        input("Press enter to quit")

    elif this_pc_os == "Linux":
        # Check
        mode = "fastfetch"
        rc, out, err = Cmd("""fastfetch""")
        if rc != 0:
            mode = "screenfetch"
        rc, out, err = Cmd("""screenfetch""")
        if rc != 0 and mode == "screenfetch":
            mode = None
            print("Please install fastfetch or screenfetch")
            import sys

            sys.exit(1)

        print("simple hw info:")
        print("cpu, cores&threads, gpu, memory, ssd, hdd")
        if mode == "screenfetch":
            rc, out, err = Cmd("""screenfetch -n -N""")
            cpu = re.search(r".*?CPU.*?:\s*(.*?)\s*\[", out).group(1)
            gpu = re.search(r".*?GPU.*?:\s*(.*?)\n", out).group(1)

        # CPU
        if mode == "fastfetch":
            rc, out, err = Cmd("""fastfetch -s cpu --format json""")
            cpu = json.loads(out)[0]["result"]["cpu"]

        # CPU detail
        rc, out, err = Cmd("""egrep '^core id' /proc/cpuinfo | sort -u | wc -l""")
        cpu_core_cnt = int(out.strip())
        rc, out, err = Cmd("""egrep '^processor' /proc/cpuinfo | sort -u | wc -l""")
        cpu_thread_cnt = int(out.strip())

        # GPU
        if mode == "fastfetch":
            rc, out, err = Cmd("""fastfetch -s gpu --format json""")
            gpus = json.loads(out)[0]["result"]
            gpu = ""
            for gpu_i in gpus:
                gpu += gpu_i["name"] + "+"
            gpu = gpu[:-1]

        # memory detail
        rc, out, err = Cmd("""sudo dmidecode --type memory""")
        out = out.split("\n\n")
        memory = ""
        memeorys = []
        for dimm in out:
            match = re.search(r"\n\s*?Type.*?:\s*(.*?)\s*\n", dimm)
            if not match:
                continue
            Type = match.group(1)
            if Type == "Unknown":
                continue
            Size = re.search(r"\s*?Size.*?:\s*(.*?)\s*GB\n", dimm).group(1)
            memeorys.append({"Type": Type, "Size": int(Size)})
            memory += Size + "+"
        # print(memeorys)
        memory = memory[:-1] + "G"
        memory_type = " (" + memeorys[0]["Type"] + ")"

        # disk
        rc, out, err = Cmd("""sudo lshw -c disk""")
        matches = re.findall(
            r"(?m)\*-disk[\S\n\t\v ]*?logical name.*?(/\S*)[\S\n\t\v ]*?size.*?\((.*)GB\)",
            out,
        )
        ssds = ""
        hdds = ""
        disks = []
        for match in matches:
            path = match[0]
            # check SSD or HDD
            rc, out, err = Cmd(f"""lsblk --raw -d -o rota {path} | tail -n 1""")
            disk = {"Path": path, "Size": match[1], "IsHDD": bool(int(out))}
            disks.append(disk)
            if disk["IsHDD"]:
                hdds += f"{int(disk['Size'])}G+"
            else:
                ssds += f"{int(disk['Size'])}G+"
        # print(disks)
        ssds = ssds[:-1] if ssds != "" else "-"
        hdds = hdds[:-1] if hdds != "" else "-"

        print(
            f"\"{cpu}, {cpu_core_cnt}C{cpu_thread_cnt}T, {gpu}, {memory}{memory_type if memory_type is not None else ''}, {ssds}, {hdds}\""
        )


if __name__ == "__main__":
    main()
