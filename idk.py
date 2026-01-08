import math as m
import time as t
import sys as s
import os as o
import random as r
import shutil as sh

# --- CẤU HÌNH ---
NoiDung = "Mano"
TocDoThuNho = 0.8
TocDoQuay = 1
SoLuong = 25

Mau_Sac = [
    (255, 182, 193), (176, 224, 230), (221, 160, 221), 
    (250, 250, 210), (152, 251, 152), (135, 206, 250)
]

def G(r1, g1, b1):
    return f'\x1b[38;2;{int(r1)};{int(g1)};{int(b1)}m'

def Rotate(v, angle_y):
    x, y, z = v
    x_new = x * m.cos(angle_y) - z * m.sin(angle_y)
    z_new = x * m.sin(angle_y) + z * m.cos(angle_y)
    return [x_new, y, z_new]

def GetCube():
    pts = []
    sc = 0.8
    vs = [[-sc,-sc,-sc],[sc,-sc,-sc],[sc,sc,-sc],[-sc,sc,-sc],
          [-sc,-sc,sc],[sc,-sc,sc],[sc,sc,sc],[-sc,sc,sc]]
    es = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    
    NoiDung_len = len(NoiDung)
    char_idx = 0
    for e in es:
        p1, p2 = vs[e[0]], vs[e[1]]
        n = int(SoLuong) 
        for i in range(n):
            rat = i / n
            pos = [p1[k] + (p2[k]-p1[k])*rat for k in range(3)]
            char = NoiDung[char_idx % NoiDung_len]
            pts.append(pos + [char]) 
            char_idx += 1
    return pts

def Main():
    o.system('') 
    o.system('cls' if o.name == 'nt' else 'clear')
    s.stdout.write('\x1b[?25l')
    target_shape = GetCube()
    N = len(target_shape)
    start_scatter = [[r.uniform(-10, 10), r.uniform(-10, 10), r.uniform(-10, 10)] for _ in range(N)]
    expl_vectors = [[t[0]*r.uniform(2, 6), t[1]*r.uniform(2, 6), t[2]*r.uniform(2, 6)] for t in target_shape]

    T_START = t.time()
    INTRO_DUR = 1.5
    
    is_exploding = False
    T_EXPLODE_START = 0
    running = True
    try:
        while running:
            curr_time = t.time()
            elapsed = curr_time - T_START
            try:
                w, h = sh.get_terminal_size((80, 24))
            except:
                w, h = 80, 24         
            cx, cy = w//2, h//2            
            buff = [[' ']*w for _ in range(h)]
            zbuff = [[-999.0]*w for _ in range(h)]
            
            pts_render = []
            s_val = 1.0 
            spin = 0.0
            
            if elapsed < INTRO_DUR:
                progress = elapsed / INTRO_DUR
                u = 1 - (1 - progress) ** 3
                spin = u * (m.pi * 4) 
                
                for i in range(N):
                    cx_p = [start_scatter[i][k] + (target_shape[i][k] - start_scatter[i][k]) * u for k in range(3)]
                    pts_render.append(cx_p + [target_shape[i][3]])
            else:
                main_t = elapsed - INTRO_DUR
                spin = main_t * TocDoQuay * 2 * m.pi
                
                beat_idx = int(main_t / TocDoThuNho)
                sub_beat = (main_t % TocDoThuNho) / TocDoThuNho
                if beat_idx >= len(NoiDung):
                    if not is_exploding:
                        is_exploding = True
                        T_EXPLODE_START = curr_time
                
                if not is_exploding:
                    pts_render = target_shape
                    if sub_beat < 0.15:
                        s_val = sub_beat / 0.15
                    elif sub_beat > 0.85:
                        s_val = (1.0 - sub_beat) / 0.15
                    else:
                        s_val = 1.0
                
                else:
                    expl_t = curr_time - T_EXPLODE_START
                    if expl_t < 0.4:
                        s_val = 1.0 - (expl_t / 0.4)
                        pts_render = target_shape
                    else:
                        real_e = expl_t - 0.4
                        s_val = 1.0
                        
                        pts_render = []
                        expansion_factor = real_e * 3.0
                        
                        for i in range(N):
                            p_orig = target_shape[i]
                            vec = expl_vectors[i]                                                 
                            new_pos = [p_orig[k] + vec[k] * expansion_factor for k in range(3)]
                            pts_render.append(new_pos + [p_orig[3]])
                        if real_e > 2.5:
                            running = False
            base_scale = h * 0.7
            final_scale = base_scale * s_val
            for i in range(len(pts_render)):
                p_raw = pts_render[i][:3]
                char = pts_render[i][3]
                p_rot = Rotate(p_raw, spin)
                cam_dist = 4.0
                z_depth = p_rot[2] + cam_dist
                if z_depth < 0.1: z_depth = 0.1              
                inv_z = 1.0 / z_depth                
                xp = int(cx + p_rot[0] * final_scale * inv_z * 2.0)
                yp = int(cy + p_rot[1] * final_scale * inv_z)
                
                if 0 <= xp < w and 0 <= yp < h:
                    if inv_z > zbuff[yp][xp]:
                        zbuff[yp][xp] = inv_z
                        c_idx = (i // 7) % len(Mau_Sac)
                        col = Mau_Sac[c_idx]
                        buff[yp][xp] = G(*col) + char
            if elapsed > INTRO_DUR:
                limit = len(NoiDung)
                if not is_exploding:
                    limit = min(beat_idx + 1, len(NoiDung))
                
                if limit > 0:
                    show_txt = NoiDung[:limit]
                    start_x = cx - len(show_txt) // 2
                    for k, ch in enumerate(show_txt):
                        if 0 <= start_x + k < w:
                            buff[cy][start_x + k] = f"\x1b[1;37m{ch}"
            out = '\x1b[H' + '\n'.join(''.join(row) for row in buff)
            s.stdout.write(out)
            s.stdout.flush()
            t.sleep(0.005)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        pass
        
    finally:
        s.stdout.write(f'\x1b[{h}H') 
        s.stdout.write('\x1b[?25h\x1b[0m\n')
if __name__ == '__main__':
    Main()
