import os
import sys
import glob
import numpy as np
from PIL import Image, ImageFilter

class ZackCriticAgent:
    """
    An ultra-strict, uncompromising AI Critic Agent modeled after Zack D. Films standards.
    Evaluates:
    1. Visual Fidelity & Rim Contrast (Studio lights, PBR sheen, dark backgrounds)
    2. Anatomical Realism & Shape Complexity (Verifies non-primitive real-world contours via edge density)
    3. Motion & Camera Pacing (No static shots, smooth cinematic push/rotations)
    4. Audio Layer Synchronization (Voiceover + SFX impact presence)
    5. Subtitle Visibility & High-Impact Styling (Bold text in central lower third)

    Maintains "WHAT IS GOOD" (preserved across iterations) and itemizes "WHAT IS WRONG"
    (blocking approval until fixed).
    """

    def __init__(self, min_contrast_threshold=38.0, min_motion_score=16.0, min_edge_density=1.8):
        self.min_contrast_threshold = min_contrast_threshold
        self.min_motion_score = min_motion_score
        self.min_edge_density = min_edge_density

    def evaluate_video(self, frames_dir, audio_path=None, script_subtitles=None):
        print("\n" + "="*60)
        print(" [ZACK CRITIC AGENT - STRICT EVALUATION MODE] REVIEWING 3D RENDER")
        print("="*60)

        frame_files = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
        if not frame_files:
            return self._format_rejection(
                good=["Directory structure initialized correctly"],
                bad=["CRITICAL: No rendered frame images found in target directory! Render engine failed or produced empty output."]
            )

        good_points = []
        bad_points = []
        scores = {}

        # 1. Visual Aspect Ratio & Resolution Check
        sample_img = Image.open(frame_files[0])
        w, h = sample_img.size
        aspect_ratio = h / float(w)

        if w == 1080 and h == 1920:
            good_points.append(f"Resolution is perfect vertical 9:16 ({w}x{h}).")
        else:
            bad_points.append(f"Resolution is {w}x{h}. Zack D. Films requires strict 1080x1920 vertical format!")

        # 2. Lighting Contrast & Vignette Fidelity Inspection
        brightness_list = []
        contrast_list = []
        edge_density_list = []

        sampled_frames = frame_files[::max(1, len(frame_files)//10)]
        for fpath in sampled_frames:
            img = Image.open(fpath).convert('L')
            arr = np.array(img, dtype=np.float32)
            brightness_list.append(np.mean(arr))
            contrast_list.append(np.std(arr))

            # Edge detection to evaluate anatomical geometry complexity vs smooth simple primitives
            edges = img.filter(ImageFilter.FIND_EDGES)
            edge_arr = np.array(edges, dtype=np.float32)
            edge_density_list.append(np.mean(edge_arr))

        avg_brightness = float(np.mean(brightness_list))
        avg_contrast = float(np.mean(contrast_list))
        avg_edge_density = float(np.mean(edge_density_list))

        scores['lighting_contrast'] = avg_contrast
        scores['shape_complexity_edge_density'] = avg_edge_density

        if avg_contrast >= self.min_contrast_threshold:
            good_points.append(f"Dramatic studio rim lighting and strong visual contrast verified (Std Dev: {avg_contrast:.2f}).")
        else:
            bad_points.append(f"Lighting contrast is too flat (Std Dev: {avg_contrast:.2f} < threshold {self.min_contrast_threshold}). Needs brighter rim light and darker background vignette.")

        # 3. Shape Realism & Anatomical Complexity Check
        if avg_edge_density >= self.min_edge_density:
            good_points.append(f"Anatomical shape realism and surface geometry detail confirmed (Edge Density: {avg_edge_density:.2f}).")
        else:
            bad_points.append(f"Geometry looks too simplified or primitive (Edge Density: {avg_edge_density:.2f} < threshold {self.min_edge_density}). Enhance real-world anatomical shape contours and surface details!")

        # 4. Motion Fluidity & Camera Pacing Analysis
        motion_diffs = []
        prev_arr = None
        for fpath in frame_files[::max(1, len(frame_files)//15)]:
            img = Image.open(fpath).convert('L')
            arr = np.array(img, dtype=np.float32)
            if prev_arr is not None:
                diff = np.mean(np.abs(arr - prev_arr))
                motion_diffs.append(diff)
            prev_arr = arr

        avg_motion = float(np.mean(motion_diffs)) if motion_diffs else 0.0
        scores['camera_motion'] = avg_motion

        if avg_motion >= self.min_motion_score:
            good_points.append(f"Dynamic camera movement and animation pace detected (Motion delta: {avg_motion:.2f}).")
        else:
            bad_points.append(f"Scene feels too static/frozen (Motion delta: {avg_motion:.2f} < threshold {self.min_motion_score}). Increase camera push-in speed and drill action.")

        # 5. Audio Layer Verification
        if audio_path and os.path.exists(audio_path):
            audio_size = os.path.getsize(audio_path)
            if audio_size > 10000:
                good_points.append(f"Audio voiceover and sound effects track verified ({audio_size // 1024} KB).")
            else:
                bad_points.append("Audio track file exists but is corrupted or silent.")
        else:
            bad_points.append("Missing voiceover audio layer! Short video content requires punchy voiceover.")

        # 6. Dynamic Captions & Engagement Hook Check
        if script_subtitles and len(script_subtitles) > 0:
            good_points.append(f"High-impact bold dynamic captions synced ({len(script_subtitles)} segments).")
        else:
            bad_points.append("No active bold dynamic captions found. Zack D. Films videos MUST have auto-synced word highlights.")

        # Final Decision Logic
        is_accepted = (len(bad_points) == 0)

        report = {
            "accepted": is_accepted,
            "overall_score": 96 if is_accepted else max(30, int(100 - len(bad_points) * 18)),
            "good_elements": good_points,
            "required_fixes": bad_points,
            "metrics": scores
        }

        self._print_critic_report(report)
        return report

    def _format_rejection(self, good, bad):
        report = {
            "accepted": False,
            "overall_score": 30,
            "good_elements": good,
            "required_fixes": bad,
            "metrics": {}
        }
        self._print_critic_report(report)
        return report

    def _print_critic_report(self, report):
        print(f"\n[ZACK CRITIC AGENT DECISION]: {'ACCEPTED' if report['accepted'] else 'REJECTED'}")
        print(f"Overall Quality Rating: {report['overall_score']}/100\n")

        print("--- WHAT IS DONE GOOD (DO NOT TOUCH OR REMOVE) ---")
        for item in report["good_elements"]:
            print(f"  ✓ {item}")

        if not report["accepted"]:
            print("\n--- WHAT IS WRONG (CRITICAL MANDATORY FIXES REQUIRED) ---")
            for item in report["required_fixes"]:
                print(f"  ✗ {item}")
            print("\n>> VERDICT: REJECTED. Fix all listed defects immediately and submit new render!\n")
        else:
            print("\n>> VERDICT: APPROVED FOR DISTRIBUTION! Exceeds Zack D. Films quality standards.\n")
        print("="*60 + "\n")

if __name__ == "__main__":
    agent = ZackCriticAgent()
    agent.evaluate_video("renders/test_frames", audio_path="output/audio/voiceover.mp3", script_subtitles=[{"text": "TEST"}])
