from pickletools import uint8

import numpy as np
import matplotlib.pyplot as plt

def damier(n, coin=0):
    f = np.ones if coin == 0 else np.zeros
    table = f((n,n), dtype=np.uint8)
    table[1::2,1::2] = coin
    table[::2,::2] = coin

    return table

def damier_bool(n, coin=False):
    f = np.ones if not coin else np.zeros
    table = f((n,n), dtype=np.bool)
    table[1::2,1::2] = coin
    table[::2,::2] = coin

    return table

def escalier(n):
    I, J = np.indices((n, n))

    return I + J

def pyramide(n):
    I, J = np.indices((n,n))

    return np.abs(I - J)

img = np.ones((16,16,3), dtype=np.uint8) * 255

y, x = np.mgrid[:16, :16]

green_mask = x < 8
img[green_mask] = [0,153,0]

crescent_mask = ((x - 8)**2 + (y - 8)**2 <= 18) & (x <= 9)
green_mask = ((x - 8)**2 + (y - 8)**2 <= 12) & (x < 8)
white_mask = ((x - 8)**2 + (y - 8)**2 <= 12) & (x >= 8)

red_color = [180, 0, 0]

img[crescent_mask] = red_color
img[green_mask] = [0,153,0]
img[white_mask] = [255,255,255]

img[8, 9] = red_color
img[8, 8] = red_color
img[9, 9] = red_color
img[8, 10] = red_color
img[7, 9] = red_color

grande = np.repeat(img, 20, 0)
grande = np.repeat(grande, 20, 1)

negative = 255 - grande

plt.imshow(negative)
plt.title("Négatif")
plt.tight_layout()
plt.show()

mirror_1 = np.fliplr(grande)

plt.imshow(mirror_1)
plt.title("Mirroir via np.fliplr")
plt.tight_layout()
plt.show()

mirror_2 = grande[::,::-1,]
plt.imshow(mirror_2)
plt.title("Mirroir via slicing")
plt.tight_layout()
plt.show()

print(f"Même image miroir ? : {np.array_equal(mirror_1, mirror_2)}")

coin = grande[:40, :40]
coin[:, :] = (0, 0, 0)
plt.imshow(grande)
plt.title("Image modifiée car fausse copie")
plt.tight_layout()
plt.show()

print("La copie de la variable est fausse: elle pointe toujours vers la même adresse mémoire")

import copy

true_copy = copy.deepcopy(grande) # ou via loop

plt.imshow(true_copy)
coin = grande[:40, :40]
coin[:, :] = (0, 0, 0)

plt.title("Image \"deepcopiée\" et intacte")
plt.tight_layout()
plt.show()

print(f"Image intacte ? : {np.array_equal(grande, true_copy)}")
print(f"Mémoire partagée ? : {np.shares_memory(grande, true_copy)}")