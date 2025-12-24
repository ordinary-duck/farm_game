# Button Image Customization Guide

## How to Use Custom Button Images

The game's button system supports custom images! You can replace the default colored buttons with your own image files.

### Button Image Requirements

1. **Supported Formats**: PNG, JPG, BMP, GIF
2. **Recommended Format**: PNG (supports transparency)
3. **Recommended Size**: 
   - Regular buttons: 300x60 pixels
   - Arrow buttons: 60x60 pixels
   - Start button: 300x60 pixels

### How to Set Custom Button Images

#### Method 1: Modify config.py

Open `config.py` and add button image paths:

```python
# Button Image Paths (optional)
BUTTON_IMAGE_START = r'assets/buttons/btn_start.png'
BUTTON_IMAGE_ARROW = r'assets/buttons/btn_arrow.png'
```

#### Method 2: Pass image_path when creating Button

In your code, create a button with custom image:

```python
# Create button with custom image
my_button = Button(
    x=100, 
    y=200, 
    width=300, 
    height=60, 
    text="Start Game",
    image_path=r'assets/buttons/my_button.png'
)
```

### Example: Customize Login Screen Buttons

Edit `login_scene.py` to use custom button images:

```python
# Previous button with custom arrow image
self.prev_button = Button(
    SCREEN_WIDTH // 2 - 220,
    SCREEN_HEIGHT // 2 - 30,
    60,
    60,
    "<",
    FONT_SIZE_LARGE,
    image_path=r'assets/buttons/arrow_left.png'  # Add this line
)

# Start button with custom image
self.start_button = Button(
    SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
    SCREEN_HEIGHT - 120,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    "Enter Game",
    FONT_SIZE_MEDIUM,
    image_path=r'assets/buttons/btn_start.png'  # Add this line
)
```

### File Path Tips

1. **Relative Path**: `assets/buttons/my_button.png`
   - The game will automatically find it relative to the game folder

2. **Absolute Path**: `D:/Images/buttons/my_button.png`
   - Use full system path

3. **Windows Path**: Use `r'path'` or double backslashes `\\`
   ```python
   r'D:\Images\button.png'  # Recommended
   'D:\\Images\\button.png'  # Also works
   ```

### Button Image Features

1. **Automatic Scaling**: Images are automatically scaled to button size
2. **Hover Effect**: Automatically creates a brighter version for hover state
3. **Fallback**: If image fails to load, uses default colored rectangle
4. **Text Overlay**: Button text is drawn on top of the image

### Troubleshooting

If button image doesn't show:

1. Check console output for error messages
2. Verify file path is correct
3. Ensure image file exists
4. Check image file format is supported
5. Try using absolute path first to test

### Example Assets Structure

```
farm_game/
©À©¤©¤ assets/
©¦   ©À©¤©¤ buttons/
©¦   ©¦   ©À©¤©¤ btn_start.png          # Start game button
©¦   ©¦   ©À©¤©¤ btn_start_hover.png    # (optional) Hover state
©¦   ©¦   ©À©¤©¤ arrow_left.png         # Left arrow
©¦   ©¦   ©À©¤©¤ arrow_right.png        # Right arrow
©¦   ©¦   ©¸©¤©¤ btn_default.png        # Default button style
©¦   ©¸©¤©¤ login_bg.jpg               # Background image
©À©¤©¤ config.py
©À©¤©¤ login_scene.py
©¸©¤©¤ main.py
```

### Tips for Creating Button Images

1. **Keep it simple**: Clear, readable designs work best
2. **High contrast**: Make sure text is visible on button
3. **Consistent style**: Use similar style for all buttons
4. **Consider hover state**: Design should work when brightened
5. **Test in game**: Try different sizes and placements

### Free Button Resources

You can find free button graphics at:
- OpenGameArt.org
- itch.io (Free Game Assets)
- Kenney.nl (Free Game Assets)
- Create your own with GIMP, Photoshop, or online tools

---

## Quick Start Example

1. Create `assets/buttons/` folder
2. Add your button image: `btn_start.png`
3. Modify button creation:

```python
self.start_button = Button(
    x=400, y=600, width=300, height=60,
    text="Start",
    image_path=r'assets/buttons/btn_start.png'
)
```

4. Run the game - your custom button will appear!

That's it! Enjoy customizing your game buttons! ??

