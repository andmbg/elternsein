import colorsys
import re
from colormath.color_objects import sRGBColor


def shift_color(css_color, saturation_factor=1.0, brightness_factor=1.0):
    # Convert CSS color to RGB
    r, g, b = int(css_color[1:3], 16), int(css_color[3:5], 16), int(css_color[5:7], 16)

    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    # Modify saturation and brightness
    s *= saturation_factor
    v *= brightness_factor

    # Clamp values to [0, 1]
    s = max(0, min(s, 1))
    v = max(0, min(v, 1))

    # Convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    # Convert to CSS color string
    modified_color = "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))

    return modified_color


def color_hex(color_str):
    """
    Turn any color representation into the hex representation and return it.
    """
    if color_str.startswith("rgba"):

        # Extract RGB values from string:
        rgba_stringparts = [value.strip() for value in color_str[5:-1].split(",")]

        # translate #1 to #3 into 0..255 integers:
        rgb_values = [int(float(value)) for value in rgba_stringparts[0:3]]

        # create sRGBColor with alpha channel:
        color = sRGBColor(*rgb_values, is_upscaled=True)

        return color.get_rgb_hex().upper()

    elif color_str.startswith("rgb"):
        
        # Extract RGB values from string:
        rgb_stringparts = [value.strip() for value in color_str[4:-1].split(",")]

        # translate into 0..255 integers:
        rgb_values = [int(float(value)) for value in rgb_stringparts]

        # create sRGBColor:
        color = sRGBColor(*rgb_values, is_upscaled=True)

        return color.get_rgb_hex().upper()

    elif color_str.startswith("#"):
        # Convert hexadecimal color to sRGBColor
        color = sRGBColor.new_from_rgb_hex(color_str[1:])

    else:
        # Handle other color representations if needed
        return None

    # Convert to hexadecimal representation
    hex_color = color.get_rgb_hex().upper()
    return hex_color


def color_rgba(color, alpha=1):
    """
    Return a string 'rgba({R}, {G}, {B}, {A}' where R/G/B are 0..255 and a is 0..1.
    """
    assert 0 <= alpha <= 1
    hex_color = color_hex(color)
    srgb_color = sRGBColor.new_from_rgb_hex(hex_color)
    rgb_tuple = (
        int(srgb_color.rgb_r * 255),
        int(srgb_color.rgb_g * 255),
        int(srgb_color.rgb_b * 255),
    )
    rgba_string = f"rgba({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]}, {alpha})"

    return rgba_string


def get_text_color(background_color):
    """
    Taking background_color as background, determine whether text displayed on it
    should be black or white. Return the color as hex string.
    """

    bgcolor_hexed = color_hex(background_color)

    # Convert hex color to RGB
    r = int(bgcolor_hexed[1:3], 16)
    g = int(bgcolor_hexed[3:5], 16)
    b = int(bgcolor_hexed[5:], 16)

    # Calculate relative luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    # Choose text color based on luminance
    if luminance > 0.5:
        return '#000000'
    else:
        return '#ffffff'


def is_valid_plotly_color(s):
    css_color_keywords = [
        "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque",
        "black", "blanchedalmond", "blue", "blueviolet", "brown", "burlywood", "cadetblue",
        "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan",
        "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkkhaki",
        "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon",
        "darkseagreen", "darkslateblue", "darkslategray", "darkturquoise", "darkviolet",
        "deeppink", "deepskyblue", "dimgray", "dodgerblue", "firebrick", "floralwhite",
        "forestgreen", "fuchsia", "gainsboro", "ghostwhite", "gold", "goldenrod", "gray",
        "green", "greenyellow", "honeydew", "hotpink", "indianred", "indigo", "ivory", "khaki",
        "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral",
        "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightpink", "lightsalmon",
        "lightseagreen", "lightskyblue", "lightslategray", "lightsteelblue", "lightyellow", "lime",
        "limegreen", "linen", "magenta", "maroon", "mediumaquamarine", "mediumblue", "mediumorchid",
        "mediumpurple", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise",
        "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "moccasin", "navajowhite",
        "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod",
        "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink",
        "plum", "powderblue", "purple", "rebeccapurple", "red", "rosybrown", "royalblue",
        "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver",
        "skyblue", "slateblue", "slategray", "snow", "springgreen", "steelblue", "tan", "teal",
        "thistle", "tomato", "turquoise", "violet", "wheat", "white", "whitesmoke", "yellow",
        "yellowgreen"
    ]

    # Define a regular expression pattern for valid Plotly colors
    pattern = re.compile(
        r"rgba?\(\s*(?:\d{1,3}\b|(?:1\d{0,2}|[1-9]?\d)\b)\s*,"
        r"\s*(?:\d{1,3}\b|(?:1\d{0,2}|[1-9]?\d)\b)\s*,"
        r"\s*(?:\d{1,3}\b|(?:1\d{0,2}|[1-9]?\d)\b)\s*"
        r"(?:,\s*(?:\d*(?:\.\d+)?|1(?:\.0+)?|\b0(?:\.0+)?\b)\s*)?\)"
    )
    return (bool(pattern.match(s))) or (s.lower() in css_color_keywords)
