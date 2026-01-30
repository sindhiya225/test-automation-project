"""
Advanced screenshot management utility for test automation framework.
Handles screenshot capture, comparison, annotation, and management.
"""
import os
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
import imagehash
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)


class ScreenshotManager:
    """
    Advanced screenshot management for test automation.
    Supports capture, comparison, annotation, and organization.
    """
    
    def __init__(self, base_dir: str = "reports/screenshots"):
        """
        Initialize screenshot manager.
        
        Args:
            base_dir: Base directory for storing screenshots
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.subdirs = {
            "failures": self.base_dir / "failures",
            "successes": self.base_dir / "successes",
            "comparisons": self.base_dir / "comparisons",
            "elements": self.base_dir / "elements",
            "archived": self.base_dir / "archived"
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)
        
        # Load font for annotation (if available)
        self.font = self._load_font()
    
    def _load_font(self) -> Optional[ImageFont.FreeTypeFont]:
        """Load font for image annotation"""
        try:
            # Try to load a system font
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "C:/Windows/Fonts/arial.ttf",  # Windows
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "arial.ttf"  # Current directory
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, 14)
            
            # Use default font if no system font found
            return ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Could not load custom font: {e}")
            return ImageFont.load_default()
    
    def capture_screenshot(self, driver, filename: Optional[str] = None, 
                          annotation: Optional[str] = None) -> str:
        """
        Capture screenshot from WebDriver.
        
        Args:
            driver: Selenium WebDriver instance
            filename: Custom filename (auto-generated if None)
            annotation: Text to annotate on screenshot
            
        Returns:
            Path to saved screenshot
        """
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                test_name = self._get_current_test_name()
                filename = f"{test_name}_{timestamp}.png"
            
            # Ensure .png extension
            if not filename.lower().endswith('.png'):
                filename += '.png'
            
            # Determine save path
            save_path = self.base_dir / filename
            
            # Capture screenshot
            driver.save_screenshot(str(save_path))
            logger.info(f"Screenshot captured: {save_path}")
            
            # Add annotation if requested
            if annotation:
                self._annotate_screenshot(save_path, annotation)
            
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return ""
    
    def capture_element_screenshot(self, driver, element, 
                                  filename: Optional[str] = None,
                                  padding: int = 10) -> str:
        """
        Capture screenshot of specific element.
        
        Args:
            driver: Selenium WebDriver instance
            element: WebElement to capture
            filename: Custom filename
            padding: Padding around element in pixels
            
        Returns:
            Path to saved screenshot
        """
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                test_name = self._get_current_test_name()
                filename = f"element_{test_name}_{timestamp}.png"
            
            # Determine save path
            save_path = self.subdirs["elements"] / filename
            
            # Get element location and size
            location = element.location
            size = element.size
            
            # Capture full screenshot first
            full_screenshot_path = self.base_dir / "temp_full.png"
            driver.save_screenshot(str(full_screenshot_path))
            
            # Crop to element
            img = Image.open(full_screenshot_path)
            
            # Calculate cropping coordinates with padding
            left = location['x'] - padding
            top = location['y'] - padding
            right = location['x'] + size['width'] + padding
            bottom = location['y'] + size['height'] + padding
            
            # Ensure coordinates are within image bounds
            left = max(0, left)
            top = max(0, top)
            right = min(img.width, right)
            bottom = min(img.height, bottom)
            
            # Crop and save
            cropped_img = img.crop((left, top, right, bottom))
            cropped_img.save(save_path)
            
            # Clean up temporary file
            if full_screenshot_path.exists():
                full_screenshot_path.unlink()
            
            logger.info(f"Element screenshot captured: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to capture element screenshot: {e}")
            return ""
    
    def capture_full_page_screenshot(self, driver, filename: Optional[str] = None) -> str:
        """
        Capture full page screenshot (including beyond viewport).
        
        Args:
            driver: Selenium WebDriver instance
            filename: Custom filename
            
        Returns:
            Path to saved screenshot
        """
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                test_name = self._get_current_test_name()
                filename = f"fullpage_{test_name}_{timestamp}.png"
            
            # Determine save path
            save_path = self.base_dir / filename
            
            # Get page dimensions
            total_width = driver.execute_script("return document.body.offsetWidth")
            total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
            
            # Set window size to capture full page
            original_size = driver.get_window_size()
            driver.set_window_size(total_width, total_height)
            
            # Capture screenshot
            driver.save_screenshot(str(save_path))
            
            # Restore original window size
            driver.set_window_size(original_size['width'], original_size['height'])
            
            logger.info(f"Full page screenshot captured: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to capture full page screenshot: {e}")
            return self.capture_screenshot(driver, filename)
    
    def capture_screenshot_with_highlights(self, driver, elements: List[Any],
                                          filename: Optional[str] = None,
                                          colors: Optional[List[str]] = None) -> str:
        """
        Capture screenshot with highlighted elements.
        
        Args:
            driver: Selenium WebDriver instance
            elements: List of WebElements to highlight
            filename: Custom filename
            colors: List of colors for highlighting
            
        Returns:
            Path to saved screenshot
        """
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                test_name = self._get_current_test_name()
                filename = f"highlighted_{test_name}_{timestamp}.png"
            
            # Determine save path
            save_path = self.base_dir / filename
            
            # Capture base screenshot
            base_path = self.base_dir / "temp_base.png"
            driver.save_screenshot(str(base_path))
            
            # Open image for annotation
            img = Image.open(base_path)
            draw = ImageDraw.Draw(img, 'RGBA')
            
            # Default colors if not provided
            if colors is None:
                colors = ['#FF000080', '#00FF0080', '#0000FF80', '#FFFF0080', '#FF00FF80']
            
            # Highlight each element
            for i, element in enumerate(elements):
                try:
                    location = element.location
                    size = element.size
                    
                    # Calculate rectangle coordinates
                    left = location['x']
                    top = location['y']
                    right = left + size['width']
                    bottom = top + size['height']
                    
                    # Draw rectangle with color
                    color = colors[i % len(colors)]
                    draw.rectangle([left, top, right, bottom], 
                                  outline=color, 
                                  fill=color,
                                  width=3)
                    
                    # Add label
                    if self.font:
                        label = f"Element {i+1}"
                        text_bbox = draw.textbbox((0, 0), label, font=self.font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]
                        
                        # Draw text background
                        text_bg_left = left
                        text_bg_top = top - text_height - 5
                        text_bg_right = left + text_width + 10
                        text_bg_bottom = top - 5
                        
                        draw.rectangle([text_bg_left, text_bg_top, 
                                       text_bg_right, text_bg_bottom],
                                       fill='#00000080')
                        
                        # Draw text
                        draw.text((left + 5, top - text_height - 5), 
                                 label, fill='white', font=self.font)
                        
                except Exception as e:
                    logger.warning(f"Failed to highlight element {i}: {e}")
            
            # Save annotated image
            img.save(save_path)
            
            # Clean up temporary file
            if base_path.exists():
                base_path.unlink()
            
            logger.info(f"Screenshot with highlights captured: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot with highlights: {e}")
            return self.capture_screenshot(driver, filename)
    
    def compare_screenshots(self, screenshot1: str, screenshot2: str, 
                           threshold: float = 0.95) -> Dict[str, Any]:
        """
        Compare two screenshots and calculate similarity.
        
        Args:
            screenshot1: Path to first screenshot
            screenshot2: Path to second screenshot
            threshold: Similarity threshold (0-1)
            
        Returns:
            Dictionary with comparison results
        """
        try:
            # Open images
            img1 = Image.open(screenshot1)
            img2 = Image.open(screenshot2)
            
            # Convert to same mode and size if needed
            if img1.mode != img2.mode:
                img2 = img2.convert(img1.mode)
            
            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
            
            # Calculate perceptual hash
            hash1 = imagehash.average_hash(img1)
            hash2 = imagehash.average_hash(img2)
            hash_similarity = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
            
            # Calculate structural similarity (SSIM)
            ssim = self._calculate_ssim(img1, img2)
            
            # Calculate pixel difference
            diff_img, diff_percentage = self._calculate_pixel_difference(img1, img2)
            
            # Save difference image if there are differences
            if diff_percentage > 0:
                diff_filename = f"diff_{Path(screenshot1).stem}_{Path(screenshot2).stem}.png"
                diff_path = self.subdirs["comparisons"] / diff_filename
                diff_img.save(diff_path)
            else:
                diff_path = None
            
            # Determine if screenshots are similar
            is_similar = hash_similarity >= threshold and ssim >= threshold
            
            result = {
                "similar": is_similar,
                "hash_similarity": float(hash_similarity),
                "ssim": float(ssim),
                "pixel_difference_percentage": float(diff_percentage),
                "threshold": threshold,
                "screenshot1": screenshot1,
                "screenshot2": screenshot2,
                "difference_image": str(diff_path) if diff_path else None,
                "image1_size": img1.size,
                "image1_mode": img1.mode,
                "image2_size": img2.size,
                "image2_mode": img2.mode
            }
            
            logger.info(f"Screenshot comparison: {result['hash_similarity']:.3f} similarity")
            return result
            
        except Exception as e:
            logger.error(f"Failed to compare screenshots: {e}")
            return {
                "similar": False,
                "error": str(e),
                "screenshot1": screenshot1,
                "screenshot2": screenshot2
            }
    
    def _calculate_ssim(self, img1: Image.Image, img2: Image.Image) -> float:
        """Calculate Structural Similarity Index (SSIM)"""
        try:
            import numpy as np
            from scipy.signal import convolve2d
            
            # Convert images to numpy arrays
            img1_arr = np.array(img1.convert('L'), dtype=np.float64)
            img2_arr = np.array(img2.convert('L'), dtype=np.float64)
            
            # Constants
            C1 = (0.01 * 255) ** 2
            C2 = (0.03 * 255) ** 2
            
            # Gaussian window
            window = self._create_gaussian_window(11, 1.5)
            window = window / np.sum(window)
            
            # Calculate means
            mu1 = convolve2d(img1_arr, window, mode='valid')
            mu2 = convolve2d(img2_arr, window, mode='valid')
            
            # Calculate variances and covariance
            mu1_sq = mu1 * mu1
            mu2_sq = mu2 * mu2
            mu1_mu2 = mu1 * mu2
            
            sigma1_sq = convolve2d(img1_arr * img1_arr, window, mode='valid') - mu1_sq
            sigma2_sq = convolve2d(img2_arr * img2_arr, window, mode='valid') - mu2_sq
            sigma12 = convolve2d(img1_arr * img2_arr, window, mode='valid') - mu1_mu2
            
            # Calculate SSIM
            ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
                       ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
            
            return float(np.mean(ssim_map))
            
        except Exception as e:
            logger.warning(f"SSIM calculation failed, using fallback: {e}")
            # Fallback to simpler similarity measure
            return 0.5
    
    def _create_gaussian_window(self, size: int, sigma: float) -> np.ndarray:
        """Create Gaussian window for SSIM calculation"""
        import numpy as np
        
        x, y = np.mgrid[-size//2 + 1:size//2 + 1, -size//2 + 1:size//2 + 1]
        g = np.exp(-((x**2 + y**2) / (2.0 * sigma**2)))
        return g / g.sum()
    
    def _calculate_pixel_difference(self, img1: Image.Image, img2: Image.Image) -> Tuple[Image.Image, float]:
        """Calculate pixel difference between two images"""
        import numpy as np
        
        # Convert to numpy arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # Calculate absolute difference
        diff = np.abs(arr1.astype(np.int16) - arr2.astype(np.int16))
        
        # Calculate percentage of different pixels
        total_pixels = arr1.size
        different_pixels = np.sum(diff > 0)
        diff_percentage = different_pixels / total_pixels
        
        # Create difference visualization
        diff_visual = np.zeros_like(arr1)
        diff_visual[diff > 0] = [255, 0, 0]  # Red for differences
        
        # Convert back to PIL Image
        diff_img = Image.fromarray(diff_visual.astype(np.uint8))
        
        return diff_img, diff_percentage
    
    def _annotate_screenshot(self, image_path: Union[str, Path], annotation: str):
        """Add annotation text to screenshot"""
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Add timestamp annotation
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_annotation = f"{annotation}\n{timestamp}"
            
            if self.font:
                # Calculate text position (top-left with padding)
                text_bbox = draw.textbbox((0, 0), full_annotation, font=self.font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Draw background rectangle
                padding = 5
                draw.rectangle([padding, padding, 
                               padding + text_width + 10, 
                               padding + text_height + 10],
                               fill='#00000080')
                
                # Draw text
                draw.text((padding + 5, padding + 5), 
                         full_annotation, fill='white', font=self.font)
            else:
                # Simple text without custom font
                draw.text((10, 10), full_annotation, fill='white')
            
            # Save annotated image
            img.save(image_path)
            logger.debug(f"Added annotation to screenshot: {annotation}")
            
        except Exception as e:
            logger.warning(f"Failed to annotate screenshot: {e}")
    
    def _get_current_test_name(self) -> str:
        """Get current test name for screenshot naming"""
        import inspect
        import sys
        
        # Try to get test name from call stack
        for frame_info in inspect.stack():
            frame = frame_info.frame
            if 'self' in frame.f_locals:
                test_instance = frame.f_locals['self']
                if hasattr(test_instance, '_testMethodName'):
                    return test_instance._testMethodName
        
        # Fallback to timestamp-based name
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def archive_screenshot(self, screenshot_path: str, reason: str = "test_completion"):
        """
        Archive screenshot to separate directory.
        
        Args:
            screenshot_path: Path to screenshot to archive
            reason: Reason for archiving
            
        Returns:
            Path to archived screenshot
        """
        try:
            path = Path(screenshot_path)
            if not path.exists():
                logger.warning(f"Screenshot not found for archiving: {screenshot_path}")
                return None
            
            # Create archive filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{path.stem}_{reason}_{timestamp}{path.suffix}"
            archive_path = self.subdirs["archived"] / archive_name
            
            # Move file
            path.rename(archive_path)
            
            logger.info(f"Screenshot archived: {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"Failed to archive screenshot: {e}")
            return None
    
    def get_screenshot_as_base64(self, screenshot_path: str) -> str:
        """
        Convert screenshot to base64 string for embedding in reports.
        
        Args:
            screenshot_path: Path to screenshot
            
        Returns:
            Base64 encoded string
        """
        try:
            with open(screenshot_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to convert screenshot to base64: {e}")
            return ""
    
    def create_screenshot_collage(self, screenshot_paths: List[str], 
                                 output_path: Optional[str] = None) -> str:
        """
        Create collage from multiple screenshots.
        
        Args:
            screenshot_paths: List of screenshot paths
            output_path: Output collage path
            
        Returns:
            Path to created collage
        """
        try:
            if not screenshot_paths:
                logger.warning("No screenshots provided for collage")
                return ""
            
            # Generate output path if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(self.base_dir / f"collage_{timestamp}.png")
            
            # Open all images
            images = []
            for path in screenshot_paths:
                if Path(path).exists():
                    img = Image.open(path)
                    # Resize to consistent width
                    img = img.resize((400, int(img.height * 400 / img.width)))
                    images.append(img)
            
            if not images:
                logger.warning("No valid screenshots for collage")
                return ""
            
            # Calculate collage dimensions
            cols = min(3, len(images))
            rows = (len(images) + cols - 1) // cols
            
            # Create collage image
            collage_width = cols * 400
            collage_height = rows * images[0].height
            
            collage = Image.new('RGB', (collage_width, collage_height), 'white')
            
            # Paste images into collage
            for i, img in enumerate(images):
                row = i // cols
                col = i % cols
                x = col * 400
                y = row * img.height
                collage.paste(img, (x, y))
            
            # Save collage
            collage.save(output_path)
            logger.info(f"Created screenshot collage: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create screenshot collage: {e}")
            return ""
    
    def clean_old_screenshots(self, days_to_keep: int = 7):
        """
        Clean up old screenshot files.
        
        Args:
            days_to_keep: Number of days to keep screenshots
        """
        try:
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
            
            deleted_count = 0
            total_size = 0
            
            # Clean all screenshot directories
            for subdir in [self.base_dir] + list(self.subdirs.values()):
                if subdir.exists():
                    for file_path in subdir.iterdir():
                        if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                            file_time = file_path.stat().st_mtime
                            if file_time < cutoff_time:
                                file_size = file_path.stat().st_size
                                file_path.unlink()
                                deleted_count += 1
                                total_size += file_size
            
            logger.info(f"Cleaned {deleted_count} old screenshots, freed {total_size/1024/1024:.2f} MB")
            
        except Exception as e:
            logger.error(f"Failed to clean old screenshots: {e}")
    
    def get_screenshot_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored screenshots.
        
        Returns:
            Dictionary with screenshot statistics
        """
        try:
            stats = {
                "total_screenshots": 0,
                "total_size_bytes": 0,
                "by_directory": {},
                "by_type": {
                    "failures": 0,
                    "successes": 0,
                    "elements": 0,
                    "comparisons": 0,
                    "archived": 0
                },
                "oldest_screenshot": None,
                "newest_screenshot": None
            }
            
            # Check all directories
            all_dirs = {"root": self.base_dir}
            all_dirs.update(self.subdirs)
            
            oldest_time = float('inf')
            newest_time = 0
            oldest_file = None
            newest_file = None
            
            for dir_name, dir_path in all_dirs.items():
                if dir_path.exists():
                    dir_stats = {
                        "count": 0,
                        "size_bytes": 0,
                        "files": []
                    }
                    
                    for file_path in dir_path.iterdir():
                        if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                            file_size = file_path.stat().st_size
                            file_time = file_path.stat().st_mtime
                            
                            dir_stats["count"] += 1
                            dir_stats["size_bytes"] += file_size
                            dir_stats["files"].append({
                                "name": file_path.name,
                                "size_bytes": file_size,
                                "modified": datetime.fromtimestamp(file_time).isoformat()
                            })
                            
                            stats["total_screenshots"] += 1
                            stats["total_size_bytes"] += file_size
                            
                            # Update oldest/newest
                            if file_time < oldest_time:
                                oldest_time = file_time
                                oldest_file = file_path
                            if file_time > newest_time:
                                newest_time = file_time
                                newest_file = file_path
                    
                    stats["by_directory"][dir_name] = dir_stats
            
            # Set oldest/newest file info
            if oldest_file:
                stats["oldest_screenshot"] = {
                    "path": str(oldest_file),
                    "modified": datetime.fromtimestamp(oldest_time).isoformat()
                }
            if newest_file:
                stats["newest_screenshot"] = {
                    "path": str(newest_file),
                    "modified": datetime.fromtimestamp(newest_time).isoformat()
                }
            
            # Update type counts from subdirectories
            for type_name, subdir in self.subdirs.items():
                if subdir.exists():
                    type_count = len([f for f in subdir.iterdir() if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.jpeg']])
                    stats["by_type"][type_name] = type_count
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get screenshot statistics: {e}")
            return {"error": str(e)}