#define eye_sep 0.76
#define y_loc 0.32
#define ana_zoom 1.3
#define WIDTH 2.4
#define BOTH 0.52
#define HEIGHT 2.4
#define palette 1.0
#define warpX 0.05
#define warpY 0.05

#if defined(VERTEX)

#if __VERSION__ >= 130
#define COMPAT_VARYING out
#define COMPAT_ATTRIBUTE in
#define COMPAT_TEXTURE texture
#else
#define COMPAT_VARYING varying 
#define COMPAT_ATTRIBUTE attribute 
#define COMPAT_TEXTURE texture2D
#endif

#ifdef GL_ES
#define COMPAT_PRECISION mediump
#else
#define COMPAT_PRECISION
#endif

COMPAT_ATTRIBUTE vec4 VertexCoord;
COMPAT_ATTRIBUTE vec4 COLOR;
COMPAT_ATTRIBUTE vec4 TexCoord;
COMPAT_VARYING vec4 COL0;
COMPAT_VARYING vec4 TEX0;

vec4 _oPosition1; 
uniform mat4 MVPMatrix;
uniform int FrameDirection;
uniform int FrameCount;
uniform COMPAT_PRECISION vec2 OutputSize;
uniform COMPAT_PRECISION vec2 TextureSize;
uniform COMPAT_PRECISION vec2 InputSize;

void main()
{
    vec4 _oColor;
    vec2 _otexCoord;
    gl_Position = VertexCoord.x * MVPMatrix[0] + VertexCoord.y * MVPMatrix[1] + VertexCoord.z * MVPMatrix[2] + VertexCoord.w * MVPMatrix[3];
    _oPosition1 = gl_Position;
    _oColor = COLOR;
    _otexCoord = TexCoord.xy;
    COL0 = COLOR;
    vec2 shift = 0.5 * InputSize / TextureSize;
    TEX0.xy = ((TexCoord.xy - shift) * ana_zoom + shift) * vec2(WIDTH, HEIGHT) - vec2(BOTH, 0.0);
}

#elif defined(FRAGMENT)

#if __VERSION__ >= 130
#define COMPAT_VARYING in
#define COMPAT_TEXTURE texture
out vec4 FragColor;
#else
#define COMPAT_VARYING varying
#define FragColor gl_FragColor
#define COMPAT_TEXTURE texture2D
#endif

#ifdef GL_ES
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
#define COMPAT_PRECISION mediump
#else
#define COMPAT_PRECISION
#endif

struct output_dummy {
    vec4 _color;
};

uniform int FrameDirection;
uniform int FrameCount;
uniform COMPAT_PRECISION vec2 OutputSize;
uniform COMPAT_PRECISION vec2 TextureSize;
uniform COMPAT_PRECISION vec2 InputSize;
uniform sampler2D Texture;
COMPAT_VARYING vec4 TEX0;
//standard texture sample looks like this: COMPAT_TEXTURE(Texture, TEX0.xy);

//distortion
vec2 Warp(vec2 pos){
  pos.xy = pos.xy * 2.0-1.0;    
  pos.xy *= vec2(1.0+(pos.y*pos.y)*warpX,1.0+(pos.x*pos.x)*warpY);
  return pos*0.5+0.5;
}

void main()
{
	output_dummy _OUT;
	vec2 warpCoord1 = Warp((TEX0.xy - vec2(eye_sep,  y_loc))*(TextureSize.xy/InputSize.xy))*(InputSize.xy/TextureSize.xy);
	vec2 warpCoord2 = Warp((TEX0.xy + vec2(eye_sep, -y_loc))*(TextureSize.xy/InputSize.xy))*(InputSize.xy/TextureSize.xy);
	vec2 fragCoord1 = warpCoord1 * InputSize / TextureSize;
	vec2 fragCoord2 = warpCoord2 * InputSize / TextureSize;
	vec4 frame1 = vec4(0.0);
	if ( fragCoord1.x < 1.0 && fragCoord1.x > 0.0 && fragCoord1.y < 1.0 && fragCoord1.y > 0.0 )
		frame1 = COMPAT_TEXTURE(Texture, warpCoord1);
	vec4 frame2 = vec4(0.0);
	if ( fragCoord2.x < 1.0 && fragCoord2.x > 0.0 && fragCoord2.y < 1.0 && fragCoord2.y > 0.0 )
		frame2 = COMPAT_TEXTURE(Texture, warpCoord2);
	frame1.r = frame1.g;
	frame2.gb = vec2(frame2.r);
	vec4 final = vec4(0.0);
	if (palette > 0.5)
		final = frame1 + frame2;
	else
		final = vec4(frame1.r + frame2.r, 0.0, 0.0, 1.0);
	_OUT._color = final;
	FragColor = _OUT._color;
	return;
} 
#endif
