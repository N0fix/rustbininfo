RULE_MINGW_6_GCC_8_3_0 = """rule rust_mingw6_gcc_8_3_0 {

  strings:

    $_ = {
        55                            //         push    rbp
        41 57                         //         push    r15
        41 56                         //         push    r14
        41 55                         //         push    r13
        41 54                         //         push    r12
        57                            //         push    rdi
        56                            //         push    rsi
        53                            //         push    rbx
        48 83 EC 38                   //         sub     rsp, 38h
        48 8D AC 24 80 00 00 00       //         lea     rbp, [rsp+80h]
        8B [5-6]                      //         mov     ebx, cs:was_init_95200
        85 DB                         //         test    ebx, ebx
        74 11                         //         jz      short loc_401CC3
        48 8D 65 B8                   //         lea     rsp, [rbp-48h]
        5B                            //         pop     rbx
        5E                            //         pop     rsi
        5F                            //         pop     rdi
        41 5C                         //         pop     r12
        41 5D                         //         pop     r13
        41 5E                         //         pop     r14
        41 5F                         //         pop     r15
        5D                            //         pop     rbp
        C3
    } // pei386_runtime_relocator


  condition:
    all of them
}"""

RULE_MINGW_7_GCC_9_3_0 = """rule rust_mingw7_gcc_9_3_0 {

    strings:
        $a = {
            55                       // push    rbp
            41 57                    // push    r15
            41 56                    // push    r14
            41 55                    // push    r13
            41 54                    // push    r12
            57                       // push    rdi
            56                       // push    rsi
            53                       // push    rbx
            48 83 EC 38              // sub     rsp, 38h
            48 8D AC 24 80 00 00 00  // lea     rbp, [rsp+80h]
            8B [5-6]                 // mov     esi, cs:was_init_93800
            85 F6                    // test    esi, esi
            74 16                    // jz      short loc_4954A8
            48 8D 65 B8              // lea     rsp, [rbp-48h]
            5B                       // pop     rbx
            5E                       // pop     rsi
            5F                       // pop     rdi
            41 5C                    // pop     r12
            41 5D                    // pop     r13
            41 5E                    // pop     r14
            41 5F                    // pop     r15
            5D                       // pop     rbp
            C3                       // retn
        } // pei386_runtime_relocator

        $b = {
            48 83 EC 28              // sub     rsp, 28h
            48 [6]                   // mov     rax, cs:_refptr_mingw_app_type
            C7 00 01 00 00 00        // mov     dword ptr [rax], 1
            E8 [4]                   // call    __security_init_cookie
            E8 [4]                   // call    __tmainCRTStartup
            90                       // nop
            90                       // nop
            48 83 C4 28              // add     rsp, 28h
            C3                       // retn
        }

    condition:
        all of them
}"""

RULE_MINGW_8_GCC_10_3_0 = """rule rust_mingw8_gcc_10_3_0 {

  strings:
        $a = {
            55                       // push    rbp
            41 57                    // push    r15
            41 56                    // push    r14
            41 55                    // push    r13
            41 54                    // push    r12
            57                       // push    rdi
            56                       // push    rsi
            53                       // push    rbx
            48 83 EC 38              // sub     rsp, 38h
            48 8D AC 24 80 00 00 00  // lea     rbp, [rsp+80h]
            8B [5-6]                 // mov     esi, cs:was_init_93800
            85 F6                    // test    esi, esi
            74 16                    // jz      short loc_4954A8
            48 8D 65 B8              // lea     rsp, [rbp-48h]
            5B                       // pop     rbx
            5E                       // pop     rsi
            5F                       // pop     rdi
            41 5C                    // pop     r12
            41 5D                    // pop     r13
            41 5E                    // pop     r14
            41 5F                    // pop     r15
            5D                       // pop     rbp
            C3                       // retn
        } // pei386_runtime_relocator

    $b = {
      48 83 EC 28                                   // sub     rsp, 28h
      48 [5-6]                          // mov     rax, cs:_refptr_mingw_app_type
      C7 00 00 00 00 00                             // mov     dword ptr [rax], 0
      E8 [4]                                // call    __tmainCRTStartup
      90                                            // nop
      90                                            // nop
      48 83 C4 28                                   // add     rsp, 28h
      C3                                            // retn
    }



  condition:
    $a and $b
}
"""

RULE_MINGW_10_GCC_12_2_0 = """rule rust_mingw10_gcc_12_2_0 {

  strings:
    $a = {
        55                     // push    rbp
        41 57                  // push    r15
        41 56                  // push    r14
        41 55                  // push    r13
        41 54                  // push    r12
        57                     // push    rdi
        56                     // push    rsi
        53                     // push    rbx
        48 83 EC 48            // sub     rsp, 48h
        48 8D 6C 24 40         // lea     rbp, [rsp+40h]
        44 [5-6]               // mov     r12d, cs:was_init_0
        45 85 E4               // test    r12d, r12d
        74 17                  // jz      short loc_1400950A8
        48 8D 65 08            // lea     rsp, [rbp+8]
        5B                     // pop     rbx
        5E                     // pop     rsi
        5F                     // pop     rdi
        41 5C                  // pop     r12
        41 5D                  // pop     r13
        41 5E                  // pop     r14
        41 5F                  // pop     r15
        5D                     // pop     rbp
        C3                     // retn
    } // pei386_runtime_relocator

    $b = {
        83 FA 10                   // cmp     edx, 10h
        0F 85 [4]                  // jnz     loc_1400954A2
        0F B7 37                   // movzx   esi, word ptr [rdi]
        81 E1 C0 00 00 00          // and     ecx, 0C0h
        66 85 F6                   // test    si, si
        0F 89 [4]                  // jns     loc_140095440
        48 81 CE 00 00 FF FF       // or      rsi, 0FFFFFFFFFFFF0000h
        48 29 C6                   // sub     rsi, rax
        4C 01 CE                   // add     rsi, r9
        85 C9                      // test    ecx, ecx
    } // pei386_runtime_relocator

    $c = {
        F3 0F 7E 81 98 00 00 00  // movq    xmm0, qword ptr [rcx+98h]
        41 0F 16 01              // movhps  xmm0, qword ptr [r9]
        0F 11 44 24 30           // movups  xmmword ptr [rsp+98h+TargetIp], xmm0
        [7-8]                    // movdqu  xmm0, cs:xmmword_1400BBFF0
        0F 11 44 24 40           // movups  xmmword ptr [rsp+98h+ReturnValue], xmm0
    } // _GCC_specific_handler rust only... Also, depends on personality

condition:
    all of them

}"""

RULE_MINGW_11_GCC_13_1_0 = """rule rust_mingw11_gcc_13_1_0 {

  strings:

    $a = {
      55                       //  push    rbp
      41 57                    //  push    r15
      41 56                    //  push    r14
      41 55                    //  push    r13
      41 54                    //  push    r12
      57                       //  push    rdi
      56                       //  push    rsi
      53                       //  push    rbx
      48 83 EC 48              //  sub     rsp, 48h
      48 8D 6C 24 40           //  lea     rbp, [rsp+40h]
      44 [5-6]                 //  mov     r12d, cs:dword_1400CC290
      45 85 E4                 //  test    r12d, r12d
      74 17                    //  jz      short loc_140097278
      48 8D 65 08              //  lea     rsp, [rbp+8]
      5B                       //  pop     rbx
      5E                       //  pop     rsi
      5F                       //  pop     rdi
      41 5C                    //  pop     r12
      41 5D                    //  pop     r13
      41 5E                    //  pop     r14
      41 5F                    //  pop     r15
      5D                       //  pop     rbp
      C3
    } // pei386_runtime_relocator
  $b = {
    83 FA 10                   // cmp     edx, 10h
    0F 85 [4]                  // jnz     loc_1400954A2
    0F B7 37                   // movzx   esi, word ptr [rdi]
    81 E1 C0 00 00 00          // and     ecx, 0C0h
    66 85 F6                   // test    si, si
    0F 89 [4]                  // jns     loc_140095440
    48 81 CE 00 00 FF FF       // or      rsi, 0FFFFFFFFFFFF0000h
    48 29 C6                   // sub     rsi, rax
    4C 01 CE                   // add     rsi, r9
    85 C9                      // test    ecx, ecx
  } // pei386_runtime_relocator

  $c = {
    F3 0F 7E 81 98 00 00 00  // movq    xmm0, qword ptr [rcx+98h]
    41 0F 16 01              // movhps  xmm0, qword ptr [r9]
    0F 29 44 24 30           // movaps  xmmword ptr [rsp+98h+var_68.cfa], xmm0
    [7-8]                    // movdqa  xmm0, cs:xmmword_1400BC040
    0F 29 44 24 40           // movaps  xmmword ptr [rsp+98h+var_68.reg], xmm0
  }
  condition:
    all of them
}"""
