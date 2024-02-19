
w_pix = 2216
h_pix = 792
panel_size  = 128
max_height  = 142

if __name__ == "__main__":

    margin = (max_height - panel_size) / 2
    width = 3 * panel_size + 2* margin
    height = panel_size + 2* margin

    print(f"box size: {width} mm x {height} mm")

    pix_pmm_x = w_pix / width
    pix_pmm_y = h_pix / height

    print(f"density x = {pix_pmm_x} y = {pix_pmm_y}")

    density = (pix_pmm_x + pix_pmm_y)/2

    print(f"avg density  = {density}")


    dx = 78 # pix
    dy = 148# pix

    dx_mm = dx/density
    dy_mm = dy/density

    print(f"dx_mm = {dx_mm} dy_mm = {dy_mm}")

    dx2 = 714 # pix
    dx_mm = dx2/density
    print(f"dx_mm = {dx_mm} dy_mm = {dy_mm}")


    print(f"teeth height = {18/density}")
