import subprocess


def run_ps_script(ps_script):
    result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
    return result.stdout, result.stderr


if __name__ == '__main__':
    print(run_ps_script('Get-Location'))
