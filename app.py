from pathlib import Path
import argparse
import numpy as np
import tifffile

# ENHANCED PALETTES v2.0
# Extracted from refined palette preview with vibrant magentas, warmer earth tones,
# and sophisticated color progressions while maintaining full color count per palette
PALETTES = {
    # HAREER HINDI-1, black-ground colorway (ENHANCED): Deep black ground with
    # vibrant magenta-to-pink progression, warm peachy mid-tones, lavender highlights
    "noir_floral_magenta": [
        (0, 7, 0),           # Deep black
        (123, 13, 58),       # Deep magenta-plum
        (208, 16, 127),      # Vibrant magenta
        (240, 80, 150),      # Hot pink-magenta
        (224, 168, 111),     # Warm peachy-gold
        (231, 153, 193),     # Warm mauve-pink
        (205, 178, 213),     # Lavender-grey
        (239, 227, 239),     # Pale lavender-white
    ],
    
    # HAREER HINDI-1, mustard/ochre-ground colorway (ENHANCED): Warm red-orange ground
    # with hot magenta accents, coral-gold mid-tones, soft cream highlights
    "golden_ochre_magenta": [
        (184, 35, 41),       # Deep warm red
        (235, 16, 106),      # Hot magenta-pink
        (218, 82, 40),       # Warm coral-red
        (190, 109, 46),      # Burnt orange
        (96, 140, 89),       # Earthy sage-green
        (231, 148, 52),      # Golden-apricot
        (233, 158, 155),     # Warm beige-rose
        (240, 220, 213),     # Cream-white
    ],
    
    # MP-47, indigo-ground colorway (ENHANCED): Rich indigo base with warm magenta
    # undertones, sophisticated purple-mauve progression to pale lavender highlight
    "regal_indigo_magenta": [
        (38, 32, 102),       # Deep indigo-purple
        (86, 37, 82),        # Rich plum-magenta
        (112, 65, 97),       # Warm purple-mauve
        (129, 80, 110),      # Sophisticated purple-grey
        (146, 95, 126),      # Warm grey-mauve
        (163, 112, 143),     # Dusty mauve-purple
        (184, 135, 164),     # Soft lavender-mauve
        (216, 184, 205),     # Pale lavender-grey
    ],
    
    # MP-47, navy-ground colorway (ENHANCED): Royal navy with purple undertones,
    # sophisticated grey-blue progression to pale powder-blue highlight
    "royal_navy_purple": [
        (63, 58, 124),       # Deep navy-purple
        (63, 58, 122),       # Royal navy
        (72, 76, 87),        # Navy-grey
        (98, 104, 118),      # Slate-blue-grey
        (118, 122, 134),     # Soft blue-grey
        (131, 135, 147),     # Pale blue-grey
        (149, 153, 165),     # Light slate-grey
        (187, 190, 195),     # Pale powder-blue
    ],
    
    # SWD-27-M, magenta/wine-ground colorway (ENHANCED): Deep warm brown shadow
    # with earthy rust progression, taupe mid-tones, pale grey-cream highlight
    "wine_poppy_earth": [
        (64, 20, 21),        # Deep brown-maroon
        (90, 45, 16),        # Warm brown-rust
        (113, 63, 30),       # Rich rust-brown
        (62, 66, 67),        # Earthy taupe-grey
        (84, 89, 93),        # Warm grey-taupe
        (109, 120, 124),     # Soft grey-taupe
        (137, 151, 151),     # Light taupe-grey
        (186, 192, 180),     # Pale grey-cream
    ],
    
    # SWD-27-M, emerald-ground colorway (ENHANCED): Deep warm brown with golden-olive
    # progression, warm earth tones, cream highlight
    "emerald_poppy_golden": [
        (77, 58, 26),        # Deep brown-ochre
        (126, 81, 14),       # Rich golden-brown
        (93, 63, 53),        # Earthy brown-taupe
        (164, 108, 25),      # Golden-ochre
        (129, 85, 72),       # Warm taupe-rust
        (166, 110, 95),      # Warm earth-taupe
        (199, 142, 122),     # Warm sand-taupe
        (227, 196, 175),     # Pale cream-sand
    ],
    
    # SWD-134, purple/teal-ground colorway (ENHANCED): Teal-blue ground with
    # magenta-red accents, olive-gold accent, warm mauve mid-tones, pale rose highlight
    "amethyst_teal_coral": [
        (0, 86, 106),        # Deep teal-blue
        (0, 121, 158),       # Rich teal-cyan
        (111, 102, 27),      # Olive-gold accent
        (126, 46, 55),       # Warm magenta-brown
        (91, 142, 173),      # Soft teal-blue
        (163, 39, 49),       # Deep magenta-coral
        (207, 91, 76),       # Warm coral-salmon
        (201, 170, 167),     # Pale mauve-rose
    ],

    # BONUS VIBRANT HYBRID: Combines best of new magenta emphasis with warm earth
    "vibrant_magenta_earth": [
        (20, 10, 15),        # Deep near-black
        (145, 20, 70),       # Vibrant magenta
        (200, 50, 100),      # Bold pink-magenta
        (220, 110, 80),      # Warm coral-pink
        (140, 130, 90),      # Warm taupe-olive
        (180, 120, 140),     # Mauve-rose
        (200, 160, 180),     # Soft lavender-rose
        (240, 225, 220),     # Cream-white
    ],
}

def rgb_to_hsl(rgb):
    """Convert RGB to HSL color space for sophisticated hue-based recoloring."""
    # NOTE: rgb is expected to already be float32 (see create_colorway). Keeping
    # every derived array in float32 (instead of the float64 numpy would use by
    # default for the divisions below) roughly halves peak memory for this step,
    # which is what was causing MemoryError on large (e.g. 4096x4096) images.
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maximum, minimum = np.max(rgb, axis=-1), np.min(rgb, axis=-1)
    lightness = (maximum + minimum) / np.float32(2.0)
    difference = maximum - minimum
    saturation = np.zeros_like(lightness)
    hue = np.zeros_like(lightness)
    nonzero = difference > 1e-12
    low_light = lightness <= 0.5
    saturation[nonzero & low_light] = difference[nonzero & low_light] / (maximum[nonzero & low_light] + minimum[nonzero & low_light])
    saturation[nonzero & ~low_light] = difference[nonzero & ~low_light] / (2.0 - maximum[nonzero & ~low_light] - minimum[nonzero & ~low_light])
    red_max = (maximum == r) & nonzero
    green_max = (maximum == g) & nonzero
    blue_max = (maximum == b) & nonzero
    hue[red_max] = ((g[red_max] - b[red_max]) / difference[red_max]) % 6.0
    hue[green_max] = ((b[green_max] - r[green_max]) / difference[green_max] + 2.0)
    hue[blue_max] = ((r[blue_max] - g[blue_max]) / difference[blue_max] + 4.0)
    hue /= 6.0
    return hue, saturation, lightness

def hue_to_rgb(p, q, t):
    """Helper function for HSL to RGB conversion."""
    t = t % 1.0
    result = np.empty_like(t)
    mask1, mask2, mask3 = t < 1.0 / 6.0, (t >= 1.0 / 6.0) & (t < 1.0 / 2.0), (t >= 1.0 / 2.0) & (t < 2.0 / 3.0)
    result[mask1] = p[mask1] + (q[mask1] - p[mask1]) * 6.0 * t[mask1]
    result[mask2] = q[mask2]
    result[mask3] = p[mask3] + (q[mask3] - p[mask3]) * (2.0 / 3.0 - t[mask3]) * 6.0
    result[~(mask1 | mask2 | mask3)] = p[~(mask1 | mask2 | mask3)]
    return result

def hsl_to_rgb(h, s, l):
    """Convert HSL back to RGB color space."""
    rgb = np.empty((*h.shape, 3), dtype=np.float32)
    achromatic = s <= 1e-12
    rgb[achromatic, 0], rgb[achromatic, 1], rgb[achromatic, 2] = l[achromatic], l[achromatic], l[achromatic]
    chromatic = ~achromatic
    q = np.empty_like(l)
    q[chromatic] = np.where(l[chromatic] < 0.5, l[chromatic] * (1.0 + s[chromatic]), l[chromatic] + s[chromatic] - l[chromatic] * s[chromatic])
    p = 2.0 * l - q
    rgb[chromatic, 0] = hue_to_rgb(p[chromatic], q[chromatic], h[chromatic] + 1.0 / 3.0)
    rgb[chromatic, 1] = hue_to_rgb(p[chromatic], q[chromatic], h[chromatic])
    rgb[chromatic, 2] = hue_to_rgb(p[chromatic], q[chromatic], h[chromatic] - 1.0 / 3.0)
    return rgb

def create_colorway(image, palette, sensitivity=1.0, saturation_boost=1.0):
    """
    Generate a new colorway by mapping source image hues to target palette.
    
    Args:
        image: Source TIFF image array
        palette: List of RGB tuples (palette colors)
        sensitivity: Controls hue shift intensity (0.0-1.0, default 1.0)
        saturation_boost: Amplifies color saturation (default 1.0, use 1.2-1.5 for vibrant results)
    
    Returns:
        Recolored image maintaining all original detail and color count
    """
    original_dtype = image.dtype
    channels = image.shape[-1]

    # Normalize to float32 [0, 1]. float32 (4 bytes/pixel/channel) instead of the
    # original float64 (8 bytes) halves the memory of every array derived below --
    # this is the fix for the MemoryError on large images. Precision loss is far
    # below what's visible in an 8- or 16-bit image, so output is unaffected.
    maximum = np.iinfo(original_dtype).max if np.issubdtype(original_dtype, np.integer) else 1.0
    normalized = image.astype(np.float32) / np.float32(maximum)
    rgb = normalized[..., :3]
    original_alpha = normalized[..., 3:4] if channels == 4 else None

    # Convert source to HSL
    orig_hue, orig_sat, orig_light = rgb_to_hsl(rgb)
    del rgb  # no longer needed once we have hue/sat/lightness; frees memory early

    # Convert palette to HSL
    palette_rgb = np.asarray(palette, dtype=np.float32) / np.float32(255.0)
    palette_hsl = [rgb_to_hsl(c[None, None, :]) for c in palette_rgb]
    palette_hues = np.array([float(h[0,0]) for h,s,l in palette_hsl])
    palette_sats = np.array([float(s[0,0]) for h,s,l in palette_hsl])

    # Find dominant hue in source (for intelligent mapping)
    hist, bin_edges = np.histogram(orig_hue[orig_sat > 0.15], bins=36, range=(0.0, 1.0))
    dominant_bin = np.argmax(hist) if len(hist) > 0 and hist.sum() > 0 else 0
    primary_orig_hue = (bin_edges[dominant_bin] + bin_edges[dominant_bin + 1]) / 2.0
    primary_target_hue = palette_hues[0]

    # Calculate hue shift with circular distance
    raw_offset = (primary_target_hue - primary_orig_hue + 0.5) % 1.0 - 0.5
    scaled_offset = raw_offset * sensitivity
    new_hue = (orig_hue + scaled_offset) % 1.0

    # Apply saturation enhancement (preserves color integrity, increases vibrancy)
    avg_target_sat = np.mean(palette_sats)
    base_saturation_shift = avg_target_sat / max(np.mean(orig_sat), 0.1)
    new_sat = np.clip(orig_sat * base_saturation_shift * saturation_boost, 0.0, 1.0)

    # Preserve lightness (maintains detail and shading)
    recolored_rgb = hsl_to_rgb(new_hue, new_sat, orig_light)

    # Combine with original alpha if present
    result = np.concatenate([recolored_rgb, original_alpha], axis=-1) if channels == 4 else recolored_rgb
    maximum = np.iinfo(original_dtype).max if np.issubdtype(original_dtype, np.integer) else 1.0
    result *= np.float32(maximum)      # in-place: avoids allocating another full-size array
    np.rint(result, out=result)
    np.clip(result, 0, maximum, out=result)
    return result.astype(original_dtype)

def read_source_metadata(path):
    """Extract TIFF metadata to preserve resolution and color space."""
    with tifffile.TiffFile(str(path)) as tf:
        page = tf.pages[0]
        tags = page.tags
        return {
            "xresolution": tags["XResolution"].value if "XResolution" in tags else None,
            "yresolution": tags["YResolution"].value if "YResolution" in tags else None,
            "resolutionunit": tags["ResolutionUnit"].value if "ResolutionUnit" in tags else None,
            "photometric": page.photometric,
            "planarconfig": page.planarconfig,
            "extrasamples": page.extrasamples if page.extrasamples else None,
        }

def main():
    parser = argparse.ArgumentParser(
        description="Professional Color Recoloring Engine v2.0 - Generate vibrant textile colorways"
    )
    parser.add_argument("--input", type=str, required=True, help="Input TIFF file path")
    parser.add_argument("--palette", type=str, required=True, help="Palette name or 'all' to generate all colorways")
    parser.add_argument("--sensitivity", type=float, default=1.0, help="Hue shift sensitivity (0.0-1.0, default 1.0)")
    parser.add_argument("--saturation", type=float, default=1.2, help="Saturation boost factor (default 1.2 for vibrant results)")
    args = parser.parse_args()

    input_file = Path(args.input)
    if not input_file.exists():
        raise FileNotFoundError(f"Cannot find input TIF file: {input_file}")

    # Load image and metadata
    image = tifffile.imread(str(input_file))
    source_meta = read_source_metadata(input_file)

    # Determine which palettes to generate
    if args.palette.lower() == "all":
        palettes_to_run = PALETTES.keys()
    elif args.palette in PALETTES:
        palettes_to_run = [args.palette]
    else:
        available = ", ".join(PALETTES.keys())
        raise ValueError(f"Palette '{args.palette}' not found. Available: {available}")

    # Generate each colorway
    print(f"Processing: {input_file.stem}")
    print(f"Sensitivity: {args.sensitivity} | Saturation Boost: {args.saturation}")
    print("-" * 70)
    
    for name in palettes_to_run:
        out_file = input_file.with_name(f"{input_file.stem}_{name}.tif")
        result = create_colorway(image, PALETTES[name], sensitivity=args.sensitivity, saturation_boost=args.saturation)
        
        # Preserve source metadata
        write_kwargs = {
            "compression": "deflate",
            "metadata": None,
            "photometric": source_meta["photometric"],
            "planarconfig": source_meta["planarconfig"],
        }
        if source_meta["xresolution"] and source_meta["yresolution"]:
            write_kwargs["resolution"] = (source_meta["xresolution"], source_meta["yresolution"])
        if source_meta["resolutionunit"]:
            write_kwargs["resolutionunit"] = source_meta["resolutionunit"]
        if image.shape[-1] == 4 and source_meta["extrasamples"]:
            write_kwargs["extrasamples"] = source_meta["extrasamples"]
        
        tifffile.imwrite(str(out_file), result, **write_kwargs)
        print(f"✓ {name:35} → {out_file.name}")

    print("-" * 70)
    print(f"Done! Generated {len(list(palettes_to_run))} colorways")

if __name__ == "__main__":
    main()
