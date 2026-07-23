# clean_bg.py
import os
import cv2
import numpy as np

def remove_background_safely(frames_dir):
    if not os.path.exists(frames_dir):
        print(f"[-] Directory '{frames_dir}' nahi mili!")
        return
        
    all_files = sorted(os.listdir(frames_dir))
    files = [os.path.join(frames_dir, f) for f in all_files if f.lower().endswith('.png')]
    
    if not files:
        print("[-] Khali folder mila! Koi PNG frames nahi hain.")
        return

    print(f"[➔] Processing {len(files)} frames... Eyes aur character pixels safe rakhe ja rahe hain.")

    for f in files:
        # Load image with alpha channel
        img = cv2.imread(f, cv2.IMREAD_UNCHANGED)
        if img is None:
            continue
            
        # Agar image me alpha channel nahi hai, toh add karo
        if img.shape[2] == 3:
            b, g, r = cv2.split(img)
            alpha = np.ones(b.shape, dtype=b.dtype) * 255
            img = cv2.merge((b, g, r, alpha))
            
        # Hoga kya: Hum binary channel nikalenge aur corner background area ko mark karenge
        # Taki character ke andar ke black pixels (eyes/clothes) modify na hon.
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
        
        # Black background ko catch karne ke liye threshold
        _, thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY_INV)
        
        # Floodfill from corners to trace outer bounds only (jaise Photoshop ka Magic Wand)
        mask = np.zeros((gray.shape[0] + 2, gray.shape[1] + 2), np.uint8)
        
        # 4 corners se seed daal kar trigger karenge
        h, w = gray.shape[:2]
        cv2.floodFill(thresh, mask, (0, 0), 255)
        cv2.floodFill(thresh, mask, (w - 1, 0), 255)
        cv2.floodFill(thresh, mask, (0, h - 1), 255)
        cv2.floodFill(thresh, mask, (w - 1, h - 1), 255)
        
        # Jo hissa floodfill se select hua, uska alpha 0 (transparent) kar do
        # Mask is offset by 1 pixel because of OpenCV layout specs
        bg_mask = mask[1:-1, 1:-1] == 1
        img[bg_mask, 3] = 0
        
        # Overwrite the original frame with clean transparent copy
        cv2.imwrite(f, img)

    print("[✔] Sabhi frames ka background clean ho gaya hai! Aankhein perfectly safe hain.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frames_folder = os.path.join(current_dir, "frames")
    remove_background_safely(frames_folder)