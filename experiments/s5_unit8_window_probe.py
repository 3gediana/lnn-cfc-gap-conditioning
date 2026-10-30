import time
now = time.time()
win_end = 1793404798
unit_deadline = now + 5400
print('now_local:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now)))
print('window_end_local:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(win_end)))
print('window_left_min: %.1f' % ((win_end - now) / 60))
print('unit_hard_deadline_local:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(unit_deadline)))
print('unit_hard_timeout_min: %.1f' % (5400 / 60))
lo, hi = 21 * 56.4, 21 * 57.9
print('train21ep_min: %.1f-%.1f' % (lo / 60, hi / 60))
print('total_est_min: %.1f-%.1f' % ((lo + 167) / 60, (hi + 167) / 60))
