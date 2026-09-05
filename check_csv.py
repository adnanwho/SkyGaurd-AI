with open('C:/Users/adnan/SkyGaurd-AI/outputs/exports/anomaly_detection_results.csv', 'r') as f:
    lines = f.readlines()
    header = lines[0].strip().split(',')
    try:
        qc_idx = header.index('qc_results')
    except ValueError:
        print('qc_results not found by simple split')
        for i, h in enumerate(header):
            if 'qc_results' in h:
                print(f'Found at index {i}: {h!r}')
        exit()
    print('qc_results at index:', qc_idx)
    parts = lines[1].strip().split(',')
    if qc_idx < len(parts):
        print('qc_results value:', parts[qc_idx][:200])
        print('Starts with quote:', parts[qc_idx].startswith('"'))
    else:
        print('OUT OF RANGE')
