# BloodVision-Tracker

**BloodVision-Tracker**: A screen filter and tracker based on PyQt5 that detects red pixels and allows interaction only within those areas.

---

## Features

- **Red Pixel Detection**: Analyzes the red pixels on the screen and highlights only those regions.
- **Soft Edges and Blinking Effect**: Creates soft edges around red areas and enables the screen to blink.
- **Python + PyQt5**: Developed using Python and PyQt5.
- **Screen Selection**: Supports multiscreen setup and allows you to choose a specific screen to work on.

---

### **Red Pixel Detection**

This section shows how red pixels are detected and how interaction is provided only in those areas. Each mode has different features.

GIFs might take a bit to load, so grab a coffee, kick back, and get ready to witness the beauty unfold!

#### 1. **Basic Mode**  
   ![Red Pixel Filter Basic](assets/gif/red_pixel_filter_basic.gif)  
   *This GIF shows how red pixels are detected and focuses only on red regions.*

#### 2. **Soft Edges**  
   ![Red Pixel Interaction](assets/gif/red_pixel_filter_smooth.gif)  
   *Interaction occurs only in the red areas on the screen, and only these regions are clickable.*

#### 3. **Soft Edges and Blinking Effect**  
   ![Red Pixel Filter Advanced](assets/gif/red_pixel_filter_fade.gif)  
   *Soft edges form around red areas, and the screen blinks.*

#### 4. **From LOL Game**  
   ![LOL Game Example](assets/gif/lol_game.gif)  
   *This GIF demonstrates how red pixels are detected and highlighted in a LOL game.*

---

### Screenshots

1. **Screen Selection and General View**  
   ![Screen Selection](assets/images/screen_set.png)  
   *Shows which screen is selected when multiple screens are present.*

---

## Installation and Usage

### Required Dependencies

- Python 3.x
- PyQt5

```bash
pip install PyQt5
```
