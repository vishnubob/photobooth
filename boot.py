#!/usr/bin/env python

import subprocess
import time
import socket
import os
import signal

class JobControl(object):
    HostJobs = {
        "sage": {
            "stt": {},
            "photolab": {},
        },
        "photobooth": {
            "photobooth": {},
            "audio": {},
            "camera": {},
            "presence": {},
            "display": {
                "sudo": True
            }
        }
    }

    def __init__(self):
        self.hostname = socket.gethostname()
        self.python_path = self.get_python_path()
        self.booth_path = self.get_booth_path()
        self.procs = {}

    def get_python_path(self):
        proc = subprocess.Popen(["which", "python"], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        return out.decode().strip()
    
    def get_booth_path(self):
        root = os.path.split(__file__)[0]
        booth_path = os.path.join(root, "booth.py")
        if not os.path.isfile(booth_path):
            raise FileNotFoundError(booth_path)
        return booth_path

    def run_job(self, job):
        msg = "Starting job '%s'" % job
        print(msg)
        cmd = [self.python_path, self.booth_path, job]
        sudo = self.HostJobs[self.hostname][job].get("sudo", False)
        if sudo:
            cmd = ["sudo"] + cmd
        proc = subprocess.Popen(cmd)
        self.procs[job] = proc

    def start(self):
        jobs = self.HostJobs[self.hostname]
        for job in jobs:
            self.run_job(job)

    def monitor(self):
        while True:
            for job in self.procs:
                proc = self.procs[job]
                if proc.poll() is not None:
                    msg = "Job '%s' is no longer running, restarting." % job
                    print(msg)
                    self.run_job(job)
            time.sleep(.1)

    def get_pids(self, job):
        proc = self.procs[job]
        ppid = str(proc.pid)
        cmd = ["ps", "-o", "pid", "--ppid", ppid, "--noheaders"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        pids = [pid.strip() for pid in out.decode().split('\n') if pid.strip()]
        pids = [ppid] + pids
        return pids

    def send_signal(self, job, level=2):
        proc = self.procs[job]
        if proc.poll():
            return
        pids = self.get_pids(job)
        level = "-%d" % level
        cmd = ["kill", level] + pids
        sudo = self.HostJobs[self.hostname][job].get("sudo", False)
        if sudo:
            cmd = ["sudo"] + cmd
        kill_proc = subprocess.Popen(cmd)
        kill_proc.wait()

    def kill(self, job, timeout=5):
        signals = [signal.SIGTERM, signal.SIGKILL]
        for level in signals:
            self.send_signal(job, level=level)
            proc = self.procs[job]
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                continue
            return

    def stop(self):
        for job in self.procs:
            proc = self.procs[job]
            self.kill(job)

if __name__ == "__main__":
    jc = JobControl()
    jc.start()
    try:
        jc.monitor()
    finally:
        jc.stop()
