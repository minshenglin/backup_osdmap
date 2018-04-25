import os
import sys
import subprocess
import json
import logging

log_path = "/var/log/osdmap_backup.log"

logging.basicConfig(level=logging.INFO, filename=log_path,
            format='[%(asctime)s][%(levelname)-5s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

def get_current_epoch():
    cmd = ["/usr/bin/ceph", "osd", "stat", "-f", "json"]
    output = subprocess.check_output(cmd)
    content = json.loads(output) 
    return int(content["epoch"])

def get_archived_epoch(path):
    epochs = os.listdir(path)
        
    if len(epochs) == 0:
        return 0

    max_epoch = -1
    for epoch in epochs:
        e = int(epoch)
        max_epoch = e if e > max_epoch else max_epoch

    return max_epoch

def backup(path, start, end):
    if start > end:
        logging.info("Archived osdmap is latest")
        return

    with open(os.devnull, 'w')  as FNULL:
        for i in range(start, end+1):
            backup_path = os.path.join(path, str(i))
            cmd = ["/usr/bin/ceph", "osd", "getmap", str(i), "-o", backup_path]
            rc = subprocess.call(cmd, stdout=FNULL, stderr=FNULL)
            logging.info("Backup osdmap epoch %s, return code is %s" % (i, rc))

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: %s <backup path>" % sys.argv[0]
        sys.exit(1)

    if os.geteuid() != 0:
        print "No root permission"
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists or not os.path.isdir(path):
        print "Illegal backup path"
        sys.exit(1)

    current = get_current_epoch()
    archived = get_archived_epoch(path)

    logging.info("Current epoch: %s" % current)
    logging.info("Archived epoch: %s" % archived)
    backup(path, archived+1, current)
