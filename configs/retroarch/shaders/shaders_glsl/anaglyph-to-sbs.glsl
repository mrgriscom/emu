// monochrome color -- use signature red
#define COLOR vec3(1,0,0)
// scale down the content by this factor
#define SCALE 1.
// extra separation between the left- and right-eye images in units of content-widths *before* scaling
// 0=perfect overlap; increasing moves the image into the screen, and decreasing moves out, but the math is kind of beyond me
#define SEP 0.

varying vec2 tex_coord;

#if defined(VERTEX)

attribute vec2 TexCoord;
attribute vec2 VertexCoord;
uniform mat4 MVPMatrix;

void main() {
    gl_Position = MVPMatrix * vec4(VertexCoord, 0.0, 1.0);
    tex_coord = TexCoord;
}

#elif defined(FRAGMENT)

uniform sampler2D Texture;

uniform vec2 OutputSize;
uniform vec2 TextureSize;
uniform vec2 InputSize;

void main() {
    // split into left and right virtual viewports
    vec2 pctViewport = tex_coord / InputSize * TextureSize;
    bool left = pctViewport.x < .5;
    pctViewport = vec2(mod(pctViewport.x * 2., 1.), pctViewport.y);

    float screen_aspect = OutputSize.x / OutputSize.y;
    float content_aspect = InputSize.x / InputSize.y;
    float x_stretch_to_screen = screen_aspect / content_aspect;

    pctViewport -= vec2(.5, .5);
    // resize to correct for original aspect ratio (display settings are such that it is initially stretched to fit
    // the entire screen -- that's the only way we can draw outside the original frame)
    pctViewport = vec2(pctViewport.x * max(x_stretch_to_screen, 1.), pctViewport.y / min(x_stretch_to_screen, 1.));
    // separation and scaling
    pctViewport = vec2(pctViewport.x + (left ? 1. : -1.) * SEP / 2., pctViewport.y);
    pctViewport *= SCALE;
    pctViewport += vec2(.5, .5);

    // sample content and decode anaglpyh
    vec4 sample = texture2D(Texture, pctViewport * InputSize / TextureSize);
    gl_FragColor = vec4(vec3(left ? sample.r : sample.g) * COLOR, 1);
}

#endif

