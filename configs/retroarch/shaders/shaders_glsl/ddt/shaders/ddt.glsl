// GLSL shader autogenerated by cg2glsl.py.
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
COMPAT_VARYING     vec2 _loc;
COMPAT_VARYING     vec4 _t1;
COMPAT_VARYING     vec2 _texCoord2;
COMPAT_VARYING     vec4 _position1;
COMPAT_VARYING     float _frame_rotation;
struct input_dummy {
    vec2 _video_size;
    vec2 _texture_size;
    vec2 _output_dummy_size;
    float _frame_count;
    float _frame_direction;
    float _frame_rotation;
};
struct out_vertex {
    vec4 _position1;
    vec2 _texCoord2;
    vec4 _t1;
    vec2 _loc;
};
out_vertex _ret_0;
input_dummy _IN1;
vec4 _r0006;
COMPAT_ATTRIBUTE vec4 VertexCoord;
COMPAT_ATTRIBUTE vec4 TexCoord;
COMPAT_VARYING vec4 TEX0;
COMPAT_VARYING vec4 TEX1;
COMPAT_VARYING vec4 TEX2;
 
uniform mat4 MVPMatrix;
uniform int FrameDirection;
uniform int FrameCount;
uniform COMPAT_PRECISION vec2 OutputSize;
uniform COMPAT_PRECISION vec2 TextureSize;
uniform COMPAT_PRECISION vec2 InputSize;
void main()
{
    out_vertex _OUT;
    vec2 _ps;
    vec2 _texCoord;
    _r0006 = VertexCoord.x*MVPMatrix[0];
    _r0006 = _r0006 + VertexCoord.y*MVPMatrix[1];
    _r0006 = _r0006 + VertexCoord.z*MVPMatrix[2];
    _r0006 = _r0006 + VertexCoord.w*MVPMatrix[3];
    _ps = vec2(1.00000000E+00/TextureSize.x, 1.00000000E+00/TextureSize.y);
    _texCoord = TexCoord.xy + vec2( 1.00000001E-07, 1.00000001E-07);
    _OUT._t1.xy = vec2(_ps.x, 0.00000000E+00);
    _OUT._t1.zw = vec2(0.00000000E+00, _ps.y);
    _OUT._loc = _texCoord*TextureSize;
    _ret_0._position1 = _r0006;
    _ret_0._texCoord2 = _texCoord;
    _ret_0._t1 = _OUT._t1;
    _ret_0._loc = _OUT._loc;
    gl_Position = _r0006;
    TEX0.xy = _texCoord;
    TEX1 = _OUT._t1;
    TEX2.xy = _OUT._loc;
    return;
    TEX0.xy = _ret_0._texCoord2;
    TEX1 = _ret_0._t1;
    TEX2.xy = _ret_0._loc;
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
COMPAT_VARYING     vec2 _loc;
COMPAT_VARYING     vec4 _t1;
COMPAT_VARYING     vec2 _texCoord;
COMPAT_VARYING     float _frame_rotation;
struct input_dummy {
    vec2 _video_size;
    vec2 _texture_size;
    vec2 _output_dummy_size;
    float _frame_count;
    float _frame_direction;
    float _frame_rotation;
};
struct out_vertex {
    vec2 _texCoord;
    vec4 _t1;
    vec2 _loc;
};
vec4 _ret_0;
float _TMP5;
float _TMP6;
vec4 _TMP4;
vec4 _TMP3;
vec4 _TMP2;
vec4 _TMP1;
vec2 _TMP0;
uniform sampler2D Texture;
vec2 _val0014;
vec2 _c0018;
vec2 _c0020;
vec2 _c0022;
float _TMP23;
float _TMP27;
float _TMP31;
float _TMP35;
float _TMP43;
vec2 _v0044;
float _TMP51;
vec2 _v0052;
float _a0060;
float _a0062;
COMPAT_VARYING vec4 TEX0;
COMPAT_VARYING vec4 TEX1;
COMPAT_VARYING vec4 TEX2;
 
uniform int FrameDirection;
uniform int FrameCount;
uniform COMPAT_PRECISION vec2 OutputSize;
uniform COMPAT_PRECISION vec2 TextureSize;
uniform COMPAT_PRECISION vec2 InputSize;
void main()
{
    vec2 _pos;
    vec2 _dir;
    vec2 _g1;
    vec2 _g2;
    vec3 _B1;
    vec3 _C1;
    vec3 _D1;
    float _p1;
    float _q1;
    float _wd1;
    float _wd2;
    vec3 _color1;
    _TMP0 = fract(TEX2.xy);
    _pos = _TMP0 - vec2( 5.00000000E-01, 5.00000000E-01);
    _val0014 = vec2(float((_pos.x > 0.00000000E+00)), float((_pos.y > 0.00000000E+00)));
    _dir = _val0014 - vec2(float((_pos.x < 0.00000000E+00)), float((_pos.y < 0.00000000E+00)));
    _g1 = _dir*TEX1.xy;
    _g2 = _dir*TEX1.zw;
    _TMP1 = COMPAT_TEXTURE(Texture, TEX0.xy);
    _c0018 = TEX0.xy + _g1;
    _TMP2 = COMPAT_TEXTURE(Texture, _c0018);
    _B1 = _TMP2.xyz;
    _c0020 = TEX0.xy + _g2;
    _TMP3 = COMPAT_TEXTURE(Texture, _c0020);
    _C1 = _TMP3.xyz;
    _c0022 = TEX0.xy + _g1 + _g2;
    _TMP4 = COMPAT_TEXTURE(Texture, _c0022);
    _D1 = _TMP4.xyz;
    _TMP23 = dot(_TMP1.xyz, vec3( 2.12599993E-01, 7.15200007E-01, 7.22000003E-02));
    _TMP27 = dot(_TMP2.xyz, vec3( 2.12599993E-01, 7.15200007E-01, 7.22000003E-02));
    _TMP31 = dot(_TMP3.xyz, vec3( 2.12599993E-01, 7.15200007E-01, 7.22000003E-02));
    _TMP35 = dot(_TMP4.xyz, vec3( 2.12599993E-01, 7.15200007E-01, 7.22000003E-02));
    _p1 = abs(_pos.x);
    _q1 = abs(_pos.y);
    _v0044 = _g1 - _pos;
    _TMP5 = dot(_v0044, _v0044);
    _TMP6 = inversesqrt(_TMP5);
    _TMP43 = 1.00000000E+00/_TMP6;
    _v0052 = _g2 - _pos;
    _TMP5 = dot(_v0052, _v0052);
    _TMP6 = inversesqrt(_TMP5);
    _TMP51 = 1.00000000E+00/_TMP6;
    _a0060 = _TMP23 - _TMP35;
    _wd1 = abs(_a0060);
    _a0062 = _TMP27 - _TMP31;
    _wd2 = abs(_a0062);
    if (_wd1 < _wd2) { 
        if (_TMP43 < _TMP51) { 
            _C1 = (_TMP1.xyz + _TMP4.xyz) - _TMP2.xyz;
        } else {
            _B1 = (_TMP1.xyz + _TMP4.xyz) - _TMP3.xyz;
        } 
    } else {
        if (_wd1 > _wd2) { 
            _D1 = (_TMP2.xyz + _TMP3.xyz) - _TMP1.xyz;
        } 
    } 
    _color1 = ((1.00000000E+00 - _p1)*(1.00000000E+00 - _q1))*_TMP1.xyz + (_p1*(1.00000000E+00 - _q1))*_B1 + ((1.00000000E+00 - _p1)*_q1)*_C1 + (_p1*_q1)*_D1;
    _ret_0 = vec4(_color1.x, _color1.y, _color1.z, 1.00000000E+00);
    FragColor = _ret_0;
    return;
} 
#endif
