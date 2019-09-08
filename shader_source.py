ps_instruction_str = """
ps_5_0
      dcl_globalFlags refactoringAllowed
      dcl_immediateConstantBuffer {
			{ 0.062745, 0.936275, 0, 0}, 
			{ 0.562745, 0.437255, 0, 0}, 
			{ 0.811765, 0.190196, 0, 0}, 
			{ 0.311765, 0.690196, 0, 0} }
      dcl_constantbuffer cb12[7], immediateIndexed
      dcl_constantbuffer cb13[1], immediateIndexed
      dcl_constantbuffer cb6[3], immediateIndexed
      dcl_constantbuffer cb7[11], immediateIndexed
      dcl_constantbuffer cb5[2], immediateIndexed
      dcl_sampler s0, mode_default
      dcl_sampler s1, mode_default
      dcl_sampler s2, mode_default
      dcl_resource_texture2d (float,float,float,float) t0
      dcl_resource_texture2d (float,float,float,float) t1
      dcl_resource_texture2d (float,float,float,float) t2
      dcl_input_ps linearCentroid v0.xy
      dcl_input_ps linearCentroid v1.w
      dcl_input_ps linearCentroid v2.xyz
      dcl_input_ps linearCentroid v3.xyzw
      dcl_input_ps_siv v4.xy, position
      dcl_input vCoverageMask
      dcl_output o0.xyzw
      dcl_output o1.xyzw
      dcl_output o2.xyzw
      dcl_output o3.xyzw
      dcl_output oMask
      dcl_temps 6
   0: mul r0.x, cb6[0].w, cb5[1].w
   1: sample_indexable(texture2d)(float,float,float,float) r1.xyzw, v0.xyxx, t0.xyzw, s0
   2: mad r0.y, r1.w, r0.x, l(-0.062745)
   3: mul r0.x, r0.x, r1.w
   4: lt r0.y, r0.y, l(0)
   5: discard_nz r0.y
   6: mul r0.yzw, r1.xxyz, r1.xxyz
   7: max r0.z, r0.w, r0.z
   8: max r0.y, r0.z, r0.y
   9: mad r1.xyz, r1.xyzx, r1.xyzx, -r0.yyyy
  10: mad r0.yzw, cb6[2].xxxx, r1.xxyz, r0.yyyy
  11: mul r0.yzw, r0.yyzw, cb6[0].xxyz
  12: max o0.xyz, r0.yzwy, l(0.003922, 0.003922, 0.003922, 0.000000)
  13: mov o0.w, r0.x
  14: and r0.y, l(0x00400000), cb13[0].x
  15: ine r0.y, r0.y, l(0)
  16: dp3 r0.z, v2.xyzx, cb12[6].xyzx
  17: lt r0.z, r0.z, l(0)
  18: movc r0.w, r0.z, l(282), l(266)
  19: and r1.x, l(6), cb7[8].w
  20: or r0.w, r0.w, r1.x
  21: or r1.x, r1.x, l(282)
  22: and r1.y, r0.w, l(4)
  23: ine r1.y, r1.y, l(0)
  24: and r0.y, r0.y, r1.y
  25: movc r0.y, r0.y, r1.x, r0.w
  26: ishl r0.y, r0.y, l(7)
  27: xor r0.y, r0.y, l(0x0000bfff)
  28: f16tof32 o1.z, r0.y
  29: mov r1.x, l(0)
  30: sample_indexable(texture2d)(float,float,float,float) r2.xyz, v0.xyxx, t1.xyzw, s1
  31: add r0.y, r2.x, l(-0.498039)
  32: mad r1.y, r0.y, l(0.250000), l(-0.001961)
  33: mad r0.yw, l(0.000000, 0.500000, 0.000000, 0.500000), r1.xxxy, l(0.000000, 0.500000, 0.000000, 0.500000)
  34: sample_indexable(texture2d)(float,float,float,float) r1.xy, v0.xyxx, t2.xyzw, s2
  35: mul r3.y, r0.w, r1.y
  36: add r0.yw, -r0.yyyw, l(0.000000, 1.000000, 0.000000, 1.000000)
  37: mov r3.x, r1.x
  38: mul r1.zw, r3.xxxy, l(0.000000, 0.000000, 1.000000, 2.000000)
  39: add r2.xw, -r1.xxxy, l(1.000000, 0.000000, 0.000000, 1.000000)
  40: lt r1.xy, r1.xyxx, l(0.500000, 0.500000, 0.000000, 0.000000)
  41: add r2.xw, r2.xxxw, r2.xxxw
  42: mad r0.yw, -r2.xxxw, r0.yyyw, l(0.000000, 1.000000, 0.000000, 1.000000)
  43: movc r0.yw, r1.xxxy, r1.zzzw, r0.yyyw
  44: mad r0.yw, r0.yyyw, l(0.000000, 2.000000, 0.000000, 2.000000), l(0.000000, -1.000000, 0.000000, -1.000000)
  45: dp2 r1.x, r0.ywyy, r0.ywyy
  46: add r1.x, -r1.x, l(1.000000)
  47: max r1.x, r1.x, l(0)
  48: sqrt r1.x, r1.x
  49: dp3 r1.y, v3.xyzx, v3.xyzx
  50: rsq r1.y, r1.y
  51: mul r1.yzw, r1.yyyy, v3.xxyz
  52: mul r3.xyz, r0.yyyy, r1.yzwy
  53: dp3 r0.y, v2.xyzx, v2.xyzx
  54: rsq r0.y, r0.y
  55: mul r4.xyz, r0.yyyy, v2.xyzx
  56: mul r5.xyz, r1.zwyz, r4.zxyz
  57: mad r5.xyz, r4.yzxy, r1.wyzw, -r5.xyzx
  58: mul r5.xyz, r5.xyzx, v3.wwww
  59: mad r3.xyz, r0.wwww, r5.xyzx, r3.xyzx
  60: mad r3.xyz, r1.xxxx, r4.xyzx, r3.xyzx
  61: dp3 r0.y, r3.xyzx, r3.xyzx
  62: rsq r0.y, r0.y
  63: mul r3.xyz, r0.yyyy, r3.xyzx
  64: movc r0.yzw, r0.zzzz, -r3.xxyz, r3.xxyz
  65: dp3 r1.x, cb12[6].xyzx, r0.yzwy
  66: mad r1.x, r1.x, l(8.000000), l(8.000000)
  67: sqrt r1.x, r1.x
  68: dp3 r3.x, cb12[4].xyzx, r0.yzwy
  69: dp3 r3.y, cb12[5].xyzx, r0.yzwy
  70: div o1.xy, r3.xyxx, r1.xxxx
  71: mov o1.w, r0.x
  72: mov o2.w, r0.x
  73: min r0.y, r2.z, l(0.996078)
  74: mul o2.z, r2.y, v1.w
  75: mad o2.x, r0.y, l(0.500000), l(0.500000)
  76: mul o2.y, cb6[1].x, cb7[10].x
  77: dp3 r2.x, cb12[4].xyzx, r1.yzwy
  78: dp3 r2.y, cb12[5].xyzx, r1.yzwy
  79: dp3 r2.z, cb12[6].xyzx, r1.yzwy
  80: lt r0.y, r2.z, l(0)
  81: movc r0.yzw, r0.yyyy, -r2.xxyz, r2.xxyz
  82: mad r0.w, r0.w, l(8.000000), l(8.000000)
  83: sqrt r0.w, r0.w
  84: div o3.xy, r0.yzyy, r0.wwww
  85: mov o3.z, cb7[6].x
  86: mov o3.w, l(0)
  87: add r0.yz, v4.xxyx, l(0.000000, -0.500000, -0.500000, 0.000000)
  88: ftou r0.yz, r0.yyzy
  89: and r0.yw, r0.yyyz, l(0, 1, 0, 1)
  90: bfi r0.z, l(1), l(1), r0.z, l(0)
  91: xor r1.x, r0.y, l(1)
  92: movc r0.y, r0.w, r1.x, r0.y
  93: iadd r0.y, r0.z, r0.y
  94: lt r0.z, icb[r0.y + 0].y, r0.x
  95: lt r0.x, icb[r0.y + 0].x, r0.x
  96: and r0.y, r0.x, l(1)
  97: bfi r0.x, l(1), l(0), r0.x, l(2)
  98: movc r0.x, r0.z, r0.x, r0.y
  99: and oMask, r0.x, vCoverageMask.x
 100: ret"""

vs_instruction_str = """
   0: add o0.xy, v6.xyxx, cb5[0].xyxx
   1: dp3 r0.x, v1.yzwy, l(1.000000, 1.000000, 1.000000, 0.000000)
   2: add r0.x, -r0.x, l(1.000000)
   3: mov r1.xyz, l(0, 0, 0, 0)
   4: imul null, r2.xyzw, values.xyzw, l(3, 3, 3, 3)
   5: round_ni r1.w, cb10[r2.x + 2].w
   6: add r3.xyzw, -r1.zzzw, cb10[r2.y + 2].xyzw
   7: mul r3.xyzw, r3.xyzw, v1.yyyy
   8: add r4.xyzw, -r1.zzzw, cb10[r2.x + 2].xyzw
   9: mad r3.xyzw, r4.xyzw, r0.xxxx, r3.xyzw
  10: add r4.xyzw, -r1.zzzw, cb10[r2.z + 2].xyzw
  11: mad r3.xyzw, r4.xyzw, v1.zzzz, r3.xyzw
  12: add r4.xyzw, -r1.zzzw, cb10[r2.w + 2].xyzw
  13: mad r3.xyzw, r4.xyzw, v1.wwww, r3.xyzw
  14: add r1.xyzw, r1.xyzw, r3.xyzw
  15: mov r3.xyz, v0.xyzx
  16: mov r3.w, l(1.000000)
  17: dp4 r4.z, r1.xyzw, r3.xyzw
  18: round_ni r5.y, cb10[r2.x + 0].w
  19: mov r5.xz, l(0, 0, 0, 0)
  20: add r6.xyzw, -r5.xxxy, cb10[r2.y + 0].xyzw
  21: mul r6.xyzw, r6.xyzw, v1.yyyy
  22: add r7.xyzw, -r5.xxxy, cb10[r2.x + 0].xyzw
  23: mad r6.xyzw, r7.xyzw, r0.xxxx, r6.xyzw
  24: add r7.xyzw, -r5.xxxy, cb10[r2.z + 0].xyzw
  25: mad r6.xyzw, r7.xyzw, v1.zzzz, r6.xyzw
  26: add r7.xyzw, -r5.xxxy, cb10[r2.w + 0].xyzw
  27: mad r6.xyzw, r7.xyzw, v1.wwww, r6.xyzw
  28: add r6.xyzw, r5.zzzy, r6.xyzw
  29: dp4 r4.x, r6.xyzw, r3.xyzw
  30: round_ni r5.w, cb10[r2.x + 1].w
  31: add r7.xyzw, -r5.zzzw, cb10[r2.y + 1].xyzw
  32: mul r7.xyzw, r7.xyzw, v1.yyyy
  33: add r8.xyzw, -r5.zzzw, cb10[r2.x + 1].xyzw
  34: mad r0.xyzw, r8.xyzw, r0.xxxx, r7.xyzw
  35: add r7.xyzw, -r5.zzzw, cb10[r2.z + 1].xyzw
  36: add r2.xyzw, -r5.zzzw, cb10[r2.w + 1].xyzw
  37: mad r0.xyzw, r7.xyzw, v1.zzzz, r0.xyzw
  38: mad r0.xyzw, r2.xyzw, v1.wwww, r0.xyzw
  39: add r0.xyzw, r5.zzzw, r0.xyzw
  40: dp4 r4.y, r0.xyzw, r3.xyzw
  41: mov o1.xyz, r4.xyzx
  42: add r2.xyz, r4.xyzx, -cb12[30].xyzx
  43: mov o1.w, v5.x
  44: mad r3.xyz, v3.xyzx, l(2.007874, 2.007874, 2.007874, 0.000000), l(-1.000000, -1.000000, -1.000000, 0.000000)
  45: dp3 o2.x, r6.xyzx, r3.xyzx
  46: dp3 o2.y, r0.xyzx, r3.xyzx
  47: dp3 o2.z, r1.xyzx, r3.xyzx
  48: mov o2.w, l(0)
  49: mad r3.xyz, v4.xyzx, l(2.007874, 2.007874, 2.007874, 0.000000), l(-1.000000, -1.000000, -1.000000, 0.000000)
  50: dp3 o3.x, r6.xyzx, r3.xyzx
  51: dp3 o3.y, r0.xyzx, r3.xyzx
  52: dp3 o3.z, r1.xyzx, r3.xyzx
  53: mad o3.w, v4.w, l(2.007874), l(-1.000000)
  54: dp3 r0.x, cb12[4].xyzx, r2.xyzx
  55: dp3 r0.y, cb12[5].xyzx, r2.xyzx
  56: dp3 r0.z, cb12[6].xyzx, r2.xyzx
  57: mov r0.w, l(1.000000)
  58: dp4 o4.x, cb12[0].xyzw, r0.xyzw
  59: dp4 o4.y, cb12[1].xyzw, r0.xyzw
  60: dp4 o4.z, cb12[2].xyzw, r0.xyzw
  61: dp4 o4.w, cb12[3].xyzw, r0.xyzw
  62: ret
"""

ps_instruction_str2 = """
   0: mul r0.x, cb5[1].w, cb6[0].w
   1: sample_indexable(texture2d)(float,float,float,float) r1.xyzw, v0.xyxx, t0.xyzw, s0
   2: mul r0.y, r0.x, r1.w
   3: mad r0.x, r1.w, r0.x, l(-0.062745)
   4: lt r0.x, r0.x, l(0)
   5: discard_nz r0.x
   6: mul r0.xzw, r1.xxyz, r1.xxyz
   7: max r0.z, r0.z, r0.w
   8: max r0.x, r0.x, r0.z
   9: mad r1.xyz, r1.xyzx, r1.xyzx, -r0.xxxx
  10: mad r0.xzw, cb6[2].xxxx, r1.xxyz, r0.xxxx
  11: mul r0.xzw, r0.xxzw, cb6[0].xxyz
  12: max o0.xyz, r0.xzwx, l(0.003922, 0.003922, 0.003922, 0.000000)
  13: dp3 r0.x, values.xyzx, cb12[6].xyzx
  14: lt r0.x, r0.x, l(0)
  15: ftou r0.w, cb7[8].w
  16: and r0.w, r0.w, l(6)
  17: ftou r1.x, cb13.x
  18: and r1.x, r1.x, l(0x00400000)
  19: iadd r1.x, r0.w, r1.x
  20: bfi r0.x, l(1), l(0), r0.x, r1.x
  21: movc r1.xy, r0.wwww, l(0.156250, 0.625000, 0.000000, 0.000000), l(0.218750, 0.875000, 0.000000, 0.000000)
  22: movc o1.z, r0.x, r1.x, r1.y
  23: sample_indexable(texture2d)(float,float,float,float) r1.xyz, v0.xyxx, t1.xyzw, s1
  24: add r0.x, r1.x, l(-0.498039)
  25: mad r2.y, r0.x, l(0.250000), l(-0.001961)
  26: mov r2.x, l(0)
  27: mad r0.xw, l(0.500000, 0.000000, 0.000000, 0.500000), r2.xxxy, l(0.500000, 0.000000, 0.000000, 0.500000)
  28: sample_indexable(texture2d)(float,float,float,float) r1.xw, v0.xyxx, t2.xzwy, s2
  29: mul r2.y, r0.w, r1.w
  30: add r0.xw, -r0.xxxw, l(1.000000, 0.000000, 0.000000, 1.000000)
  31: mov r2.x, r1.x
  32: mul r2.xy, r2.xyxx, l(1.000000, 2.000000, 0.000000, 0.000000)
  33: add r2.zw, -r1.xxxw, l(0.000000, 0.000000, 1.000000, 1.000000)
  34: lt r1.xw, r1.xxxw, l(0.500000, 0.000000, 0.000000, 0.500000)
  35: add r2.zw, r2.zzzw, r2.zzzw
  36: mad r0.xw, -r2.zzzw, r0.xxxw, l(1.000000, 0.000000, 0.000000, 1.000000)
  37: movc r0.xw, r1.xxxw, r2.xxxy, r0.xxxw
  38: mad r0.xw, r0.xxxw, l(2.000000, 0.000000, 0.000000, 2.000000), l(-1.000000, 0.000000, 0.000000, -1.000000)
  39: dp2 r1.x, r0.xwxx, r0.xwxx
  40: add r1.x, -r1.x, l(1.000000)
  41: max r1.x, r1.x, l(0)
  42: dp3 r1.w, v3.xyzx, v3.xyzx
  43: sqrt r1.xw, r1.xxxw
  44: div r1.w, l(1.000000, 1.000000, 1.000000, 1.000000), r1.w
  45: mul r2.xyz, r1.wwww, v3.zxyz
  46: mul r3.xyz, r0.xxxx, r2.yzxy
  47: dp3 r0.x, values.xyzx, values.xyzx
  48: sqrt r0.x, r0.x
  49: div r0.x, l(1.000000, 1.000000, 1.000000, 1.000000), r0.x
  50: mul r4.xyz, r0.xxxx, values.xyzx
  51: mul r5.xyz, r2.zxyz, r4.zxyz
  52: mad r2.xyz, r4.yzxy, r2.xyzx, -r5.xyzx
  53: mul r2.xyz, r2.xyzx, v3.wwww
  54: mad r2.xyz, r0.wwww, r2.xyzx, r3.xyzx
  55: mad r2.xyz, r1.xxxx, r4.xyzx, r2.xyzx
  56: dp3 r0.x, r2.xyzx, r2.xyzx
  57: sqrt r0.x, r0.x
  58: div r0.x, l(1.000000, 1.000000, 1.000000, 1.000000), r0.x
  59: mul r2.xyz, r2.xyzx, r0.xxxx
  60: ne r0.x, l(0, 0, 0, 0), r0.z
  61: movc r0.xzw, r0.xxxx, -r2.xxyz, r2.xxyz
  62: dp3 r1.x, cb12[6].xyzx, r0.xzwx
  63: mad r1.x, r1.x, l(8.000000), l(8.000000)
  64: sqrt r1.x, r1.x
  65: dp3 r2.x, cb12[4].xyzx, r0.xzwx
  66: dp3 r2.y, cb12[5].xyzx, r0.xzwx
  67: div o1.xy, r2.xyxx, r1.xxxx
  68: min r0.x, r1.z, l(0.996078)
  69: mul o2.z, r1.y, v1.w
  70: mad o2.x, r0.x, l(0.500000), l(0.500000)
  71: mul o2.y, cb6[1].x, cb7[10].x
  72: mov o0.w, r0.y
  73: mov o1.w, r0.y
  74: mov o2.w, r0.y
  75: mov oMask, l(7)
  76: ret
"""
