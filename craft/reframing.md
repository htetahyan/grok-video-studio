# Reframing between formats

| preset | fit | when |
|---|---|---|
| master-16x9 | cover (scale + center crop) | landscape sources |
| reel-9x16 | blur-pad (sharp 16:9 over a soft, darkened fill of itself) | landscape sources you can't crop without losing the subject |
| square-1x1 | cover | most feed posts |
| review-720p | fit-pad + burned timecode | review proxies only |

- `blur-pad` is a safe default, not the best result. For hero reels, reframe by hand: crop to the subject,
  key the crop position through the shot, and render that conform as a bench file before `fw render`.
- Vertical-native footage should render to reel-9x16 with `cover`, so there are no bars at all.
- Check the 9:16 safe zone: keep text and faces away from the top 12% and bottom 20%, where platform UI sits.
