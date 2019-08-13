import cv2
import numpy as np
import argparse
import os
import shutil
import tqdm

class CoordinateStore():
    def __init__(self):
        self.coords = []

    def click_select(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            self.coords.append((x, y))
    
    def clear_coords(self):
        self.coords = []

def coord_to_grid(image, coord, grid):
    x, y = coord
    i, j = grid
    h, w, _ = image.shape
    return int(x/w*i), int(y/h*j)

def grid_coord_to_section(image, grid_coord, grid):
    c, r = grid_coord
    i, j = grid
    h, w, _ = image.shape
    c_width = w//i      # width of each column, in pixels
    r_height = h//j      # height of each column
    section = image[r_height*r:r_height*(r+1), c_width*c:c_width*(c+1)]
    return section

def slice_all(indir, outdir):
    for d in os.listdir(indir):
        d_path = os.path.join(indir, d)
        if not os.path.isdir(d_path):
            continue
        for f in tqdm.tqdm(os.listdir(d_path)):
            image = cv2.imread(os.path.join(d_path, f))
            img_base = os.path.splitext(f)[0]
            all_coords = set([(0, 0), (0, 1), (1, 0), (1, 1)])
            for c, r in all_coords:
                section = grid_coord_to_section(image, (c, r), (2, 2))
                cv2.imwrite(os.path.join(outdir, img_base+'_{}_{}_{}.jpg'.format(c, r, d)), section)

def classify_sections(indir, outdir):
    cv2.namedWindow('tile')
    store = CoordinateStore()
    cv2.setMouseCallback('tile', store.click_select)

    for d in os.listdir(indir):
        d_path = os.path.join(indir, d)
        if not os.path.isdir(d_path):
            continue
        for f in os.listdir(d_path):
            store.clear_coords()
            img_base = os.path.splitext(f)[0]
            image = cv2.imread(os.path.join(d_path, f))
            img_guides = image
            cv2.line(img_guides, (image.shape[0]//2, 0), (image.shape[0]//2, image.shape[1]), (255,0,0), 2)
            cv2.line(img_guides, (0, image.shape[1]//2), (image.shape[0], image.shape[1]//2), (255,0,0), 2)
            cv2.imshow('tile', img_guides)
            all_coords = set([(0, 0), (0, 1), (1, 0), (1, 1)])
            key = cv2.waitKey(0) & 0xFF
            if key==ord(' '):
                for coord in store.coords:
                    c, r = coord_to_grid(image, coord, (2, 2))
                    if (c, r) in all_coords:
                        section = grid_coord_to_section(image, (c, r), (2, 2))
                        all_coords.remove((c, r))
                        cv2.imwrite(os.path.join(outdir, 'm', img_base+'_{}_{}.jpg'.format(c, r)), section)
                for coord in all_coords:
                    if coord not in store.coords:
                        c, r = coord
                        section = grid_coord_to_section(image, (c, r), (2, 2))
                        cv2.imwrite(os.path.join(outdir, 'nm', img_base+'_{}_{}.jpg'.format(c, r)), section)
                continue
            if key==ord('q'):
                break
    cv2.destroyAllWindows()


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--indir', help='input directory')
    parser.add_argument('--outdir', help='output directory')
    parser.add_argument('--nm', action='store_true', help='mark clicked sections as nm')
    args = parser.parse_args()

    indir = os.path.abspath(args.indir)
    outdir = os.path.abspath(args.outdir)
    # classify_sections(indir, outdir)
    slice_all(indir, outdir)
