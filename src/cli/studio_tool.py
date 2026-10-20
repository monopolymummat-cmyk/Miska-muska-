import os
import sys
import json
import subprocess
import asyncio
from src.audio.audio_engine import generate_voiceover, generate_sound_effects
from src.critic.critic_agent import ZackCriticAgent

class ZackVideoCreatorStudio:
    """
    Unified Creator Tool Suite that orchestrates:
    3D WebGL Scene Generation -> Node.js Frame Rendering -> Audio Synthesis -> FFmpeg Video Assembly -> Strict Critic Evaluation Loop.
    """

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.renders_dir = os.path.join(output_dir, "renders")
        self.audio_dir = os.path.join(output_dir, "audio")
        self.video_dir = os.path.join(output_dir, "videos")

        os.makedirs(self.renders_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)

        self.critic = ZackCriticAgent(min_contrast_threshold=30.0, min_motion_score=10.0)

    async def create_video(self, topic_title, script_text, subtitles, duration_sec=6.0, fps=30, max_attempts=3):
        print("\n" + "#"*60)
        print(f" CREATING 3D VIDEO SHORT: {topic_title.upper()}")
        print("#"*60)

        # Step 1: Synthesize Audio & SFX
        vo_path = os.path.join(self.audio_dir, "voiceover.mp3")
        sfx_path = os.path.join(self.audio_dir, "sfx.wav")

        await generate_voiceover(script_text, vo_path)
        generate_sound_effects(duration_sec, sfx_path)

        for attempt in range(1, max_attempts + 1):
            print(f"\n--- RENDERING & EVALUATION ATTEMPT {attempt}/{max_attempts} ---")

            # Step 2: Render 3D WebGL Frames using Node Playwright Driver
            scene_config = {
                "title": topic_title,
                "subtitles": subtitles
            }

            config_path = os.path.join(self.renders_dir, "scene_config.json")
            with open(config_path, "w") as f:
                json.dump(scene_config, f, indent=2)

            frames_dir = os.path.join(self.renders_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)

            render_frames_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "renderer", "render_frames.js"))

            # Use json.dumps to safely convert file paths for cross-platform JavaScript string literals
            js_render_path = json.dumps(render_frames_path)
            js_config_path = json.dumps(config_path)
            js_frames_dir = json.dumps(frames_dir)

            node_script = f"""
const {{ render3DVideo }} = require({js_render_path});
const fs = require('fs');

const sceneConfig = JSON.parse(fs.readFileSync({js_config_path}, 'utf8'));

render3DVideo({{
    sceneConfig,
    outputFramesDir: {js_frames_dir},
    fps: {fps},
    duration: {duration_sec}
}}).then(() => console.log('[Studio] Node rendering step completed.'))
  .catch(err => {{ console.error('[Studio] Node rendering error:', err); process.exit(1); }});
"""
            runner_path = os.path.join(self.renders_dir, "run_render.js")
            with open(runner_path, "w") as f:
                f.write(node_script)

            print("[Studio] Launching WebGL 3D frame renderer...")
            subprocess.run(["node", runner_path], check=True)

            # Step 3: Run Strict Quality Critic Review
            print("\n[Studio] Sending rendered frames to Strict Critic Agent for Review...")
            critic_report = self.critic.evaluate_video(
                frames_dir=frames_dir,
                audio_path=vo_path,
                script_subtitles=subtitles
            )

            if critic_report["accepted"]:
                print(f"\n[CRITIC APPROVED ATTEMPT {attempt}]: Video met all quality standards!")

                # Step 4: Assemble Final MP4 with FFmpeg (Audio + SFX + Frames)
                final_mp4 = os.path.join(self.video_dir, f"{topic_title.lower().replace(' ', '_')}_zack.mp4")

                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-framerate", str(fps),
                    "-i", os.path.join(frames_dir, "frame_%05d.png"),
                    "-i", vo_path,
                    "-i", sfx_path,
                    "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                    "-map", "0:v",
                    "-map", "[aout]",
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-preset", "fast",
                    "-crf", "18",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    final_mp4
                ]

                print(f"[Studio] Assembling high quality MP4 video to {final_mp4}...")
                subprocess.run(ffmpeg_cmd, check=True)

                print(f"\n[SUCCESS] Video accepted by Agent and created successfully: {final_mp4}")
                return True, critic_report, final_mp4

            else:
                print(f"\n[CRITIC REJECTED ATTEMPT {attempt}]: Preserving good elements: {critic_report['good_elements']}")
                print(f"Items to fix: {critic_report['required_fixes']}")
                if attempt == max_attempts:
                    print("\n[CRITIC MAX ATTEMPTS REACHED]: Video refused final MP4 build.")
                    return False, critic_report, None

if __name__ == "__main__":
    studio = ZackVideoCreatorStudio()
    subtitles = [
        {"start": 0.2, "end": 2.5, "text": "WHAT HAPPENS WHEN CAVITIES DRILL DEEP?"},
        {"start": 2.6, "end": 4.5, "text": "THE DRILL REMOVES DECAYED ENAMEL"},
        {"start": 4.6, "end": 5.8, "text": "PREVENTING PERMANENT NERVE DAMAGE!"}
    ]
    script = "What happens when cavities drill deep? The drill removes decayed enamel, preventing permanent nerve damage!"

    asyncio.run(studio.create_video("Tooth Cavity Drill", script, subtitles, duration_sec=6.0))
