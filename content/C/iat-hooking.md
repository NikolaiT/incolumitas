Title: IAT hooking
Date: 2013-12-07 11:37
Author: Nikolai Tschacher
Category: C
Tags: C, Hooking, Programming, Security, Windows, Nt, Assembler, Iat
Slug: iat-hooking
Status: published

### What

I just rummaged through my old hard disk and suddenly stumbled across
some old C sources from around a year ago when I played with IAT hooking
on windows 7. I will not explain much, but I made the bottom code around
a year ago (Thus, in 2012) and it should be able to hook any code
(depicted as the handler here) into running processes via the IAT. I
suppose the code is not working properly, but it gives a good picture of
how an IAT hooking approach might look like.

### [What'll you do?](http://www.youtube.com/watch?v=432PZ9787n0)

Hopefully I'll find some time and motivation (or more appropriate:
discipline) to update the little library and finally complete it. Maybe
I will also make it compatible with windows 8, but I assume it's not
really different from windows 7 (Hell I don't know anything about the
windows API)...

    :::C
    #include "main.h"

    /* 
     * Implements a little library to Hook the WinApi on running programs.
     * Furthermore, the API provides functions too find code caves and little hook templates for the most common scenarios
     * when we use hooking: Intercept function parameters and monitor output...
     * Supports both, 32 and 64 bit Windows XP to Windows 7. The code is pretty bloated, because
     * I intended to catch as many errors as possbible and included some debug stuff. This hooking 'library' shall be reliable.
     * It provides just IAT hooking, no other code injections.
     */

    int
    main(int argc, char *argv[])
    {
        HANDLE hProcess;
        HOOK_CONTEXT *pHookContext;
        DWORD pid;
        BOOL bSuccess;

        char* handler =
            "\x90\x90\x90\x90\x90\x90\x90\x90"
            "\x90\x90\x90\x90\x90\x90\x90\x90"
            "\x90\x90\x90\x90\x90\x90\x90\x90";

    #ifdef _WIN64
        printf("[i] 64 architecture detected\n");
        fprintf(stderr, "[-] Sorry, currently not supported\n");
        exit(EXIT_FAILURE);
    #endif

    #ifdef _WIN32
        printf("[i] 32 architecture detected\n");
    #endif

        if (argc < 2) {
            pid = GetCurrentProcessId();
            printf("[i] using current process id as target\n");
        } else if (argc >= 2) {
            pid = (DWORD) atoi(argv[1]);
        } else {
            fprintf(stderr, "Usage: %s PID", argv[0]);
            exit(EXIT_FAILURE);
        }

        /* Try to open the specified process */
        hProcess = OpenProcess
        (
            PROCESS_QUERY_INFORMATION |
            PROCESS_VM_OPERATION |
            PROCESS_VM_READ |
            PROCESS_VM_WRITE |
            PROCESS_SET_QUOTA,
            FALSE,
            pid
        );

        if (hProcess == NULL) {
            fprintf(stderr, "[!] OpenProcess() failed with %d\n", GetLastError());
            exit(EXIT_FAILURE);
        } else {
            printf("[i] Remote Process with PID=%d opened\n", pid);
        }

        /* Hook shit */
        pHookContext = HookFunction
        (
            hProcess,
            "USER32.DLL",
            "MessageBoxA",
            handler,
            strlen(handler)
        );

        if (pHookContext == NULL) {
            fprintf(stderr, "[!] Hooking failed\n", GetLastError());
            exit(EXIT_FAILURE);
        } else
            printf("[i] hooked\n", pid);


        Sleep(50000); // Sleep 60 seconds. Try now the new behaviour of the function :)

        bSuccess = ReleaseHook
        (
            hProcess,
            pHookContext
        );

        if (!bSuccess) {
            fprintf(stderr, "[!] Release Hook failed\n", GetLastError());
            exit(EXIT_FAILURE);
        } else
            printf("[i] Hook released\n", pid);

        CloseHandle(hProcess);
        exit(EXIT_SUCCESS);
    }

    // =============================================================================================

    DWORD
    FindRemotePEB(HANDLE hProcess)
    {
        HMODULE hNTDll;
        FARPROC fpNtQueryInformationProcess;
        NTSTATUS status;
        PROCESS_BASIC_INFORMATION procBasicInformation;
        ULONG returnLength;

        hNTDll = LoadLibraryA("ntdll");

        if (!hNTDll) {
            fprintf(stderr, "LoadLibraryA() failed with %d\n", GetLastError());
            return 0;
        }

        fpNtQueryInformationProcess = GetProcAddress
        (
            hNTDll,
            "NtQueryInformationProcess"
        );

        if (!fpNtQueryInformationProcess) {
            fprintf(stderr, "GetProcAddress() failed with %d\n", GetLastError());
            return 0;
        }

        NtQueryInformationProcess ntQueryInformationProcess = 
            (NtQueryInformationProcess)fpNtQueryInformationProcess;

        status = ntQueryInformationProcess
        (
            hProcess,
            0, // ProcessBasicInformation
            &procBasicInformation,
            sizeof(PROCESS_BASIC_INFORMATION),
            &returnLength
        );

        if (status != 0) {
            fprintf(stderr, "NtQueryInformationProcess() failed with %d\n", status);
            return 0;
        }

        return (DWORD)procBasicInformation.PebBaseAddress;
    }

    // =============================================================================================

    /* Get's the PEB of the own process */
    DWORD 
    FindOwnPEB(void)
    {
        DWORD pebAddr;

    #ifdef _WIN32
        _asm 
        {
            push eax // push the values of the register eax on the stack
            mov eax, FS:[0x30] // store the values ad address FS:[0x30] in eax
            mov [pebAddr], eax // store the values of eax in the variable pebAddr
            pop eax // remake initial eax value
        }
    #endif

    #ifdef _WIN64
        _asm
        {
            push rax
            mov rax, FS:[0x30]
            mov [pebAddr], rax
            pop rax
        }
    #endif

        return pebAddr;
    }

    // =============================================================================================

    PIMAGE_DATA_DIRECTORY
    ReadRemoteDataDirectoryRVA(HANDLE hProcess, LPCVOID lpImageBaseAddress, DWORD index)
    {
        PIMAGE_NT_HEADERS32 pNTHeaders;
        PIMAGE_DATA_DIRECTORY dataDir;
        BYTE* lpBuffer;
        DWORD oldProtect;

        if (index < 0 || index > 16) {
            fprintf(stderr, "No valid DATA_DIRECTORY directory\n");
            return 0;
        }

        lpBuffer = malloc(sizeof(BUFFER_SIZE));
        ZeroMemory(lpBuffer, BUFFER_SIZE);

        if (lpBuffer == NULL) {
            fprintf(stderr, "malloc() failed with %d\n", GetLastError());
            return 0;
        }

        BOOL bSuccess = VirtualProtectEx
        (
            hProcess,
            (PVOID)lpImageBaseAddress,
            BUFFER_SIZE,
            PAGE_EXECUTE_READ,
            &oldProtect
        );

        if (!bSuccess) {
            fprintf(stderr, "VirtualProtectEx() failed in ReadRemoteDataDirectoryRVA() with %d\n", GetLastError());
            return 0;
        }

        bSuccess = ReadProcessMemory
        (
            hProcess,
            lpImageBaseAddress,
            lpBuffer,
            BUFFER_SIZE,
            0
        );

        if (!bSuccess) {
            fprintf(stderr, "ReadProcessMemory() failed in ReadRemoteDataDirectoryRVA() with %d\n", GetLastError());
            return 0;
        }

        PIMAGE_DOS_HEADER pDOSHeader = (PIMAGE_DOS_HEADER)lpBuffer;

        if (pDOSHeader->e_magic != 0x5a4d) {
            fprintf(stderr, "Invalid DOS header. e_magic is not  0x5a4d\n");
            return 0;
        }

        pNTHeaders = (PIMAGE_NT_HEADERS32)(lpBuffer + pDOSHeader->e_lfanew);

        if (pNTHeaders->OptionalHeader.Magic != 0x10b && // PE32
            pNTHeaders->OptionalHeader.Magic != 0x20b) { // PE32+
            fprintf(stderr, "Invalid Magic in OptionalHeader\n");
            return NULL;
        } else 
            printf("[i] Detected %s architecture\n",
                 pNTHeaders->OptionalHeader.Magic == 0x10b ? "PE32" : "PE32+");

        dataDir = &pNTHeaders->OptionalHeader.DataDirectory[index];

        return dataDir;
    }

    // =============================================================================================

    /*
     * Caller has to free the returned LOADED_IMAGE structure.
     */
    PLOADED_IMAGE ReadRemoteImage(HANDLE hProcess, LPVOID lpImageBaseAddress)
    {
        PCHAR lpBuffer;
        PIMAGE_DOS_HEADER pDOSHeader;
        PLOADED_IMAGE pImage;

        BOOL bSuccess = RetReadProcessMemory
        (
            &lpBuffer,
            hProcess,
            lpImageBaseAddress,
            BUFFER_SIZE
        );

        if (!bSuccess) {
            fprintf(stderr, "RetReadProcessMemory() failed in ReadRemoteImage() with %d\n", GetLastError());
            return NULL;
        }

        pDOSHeader = (PIMAGE_DOS_HEADER)lpBuffer;

        pImage = malloc(sizeof(LOADED_IMAGE));

        if (pImage == NULL) {
            fprintf(stderr, "malloc() failed in ReadRemoteImage() with %d\n", GetLastError());
            return NULL;
        }

        pImage->FileHeader = 
            (PIMAGE_NT_HEADERS32)(lpBuffer + pDOSHeader->e_lfanew);

        pImage->NumberOfSections = 
            pImage->FileHeader->FileHeader.NumberOfSections;

        pImage->Sections = 
            (PIMAGE_SECTION_HEADER)(lpBuffer + pDOSHeader->e_lfanew + 
            sizeof(IMAGE_NT_HEADERS32));

        if (pDOSHeader->e_magic != 0x5a4d) {
            fprintf(stderr, "Invalid DOS header. e_magic is not  0x5a4d\n");
            return NULL;
        }

        if (pImage->FileHeader->OptionalHeader.Magic != 0x10b && // PE32
            pImage->FileHeader->OptionalHeader.Magic != 0x20b) { // PE32+
            fprintf(stderr, "Invalid Magic in OptionalHeader\n");
            return NULL;
        } else 
            printf("[i] Detected %s architecture\n",
                 pImage->FileHeader->OptionalHeader.Magic == 0x10b ? "PE32" : "PE32+");

        return pImage;
    }
    // =============================================================================================

    PIMAGE_SECTION_HEADER FindSectionHeaderByName(PIMAGE_SECTION_HEADER pHeaders, 
                                                  DWORD dwNumberOfSections, LPCTSTR pSectionName)
    {
        PIMAGE_SECTION_HEADER pHeaderMatch = NULL;

        for (DWORD i = 0; i < dwNumberOfSections; i++) {
            PIMAGE_SECTION_HEADER pHeader = &pHeaders[i];

            if (_stricmp((char*)pHeader->Name, pSectionName) == 0) {
                pHeaderMatch = pHeader;
                break;
            }
        }   

        return pHeaderMatch;
    }

    /*
     * Finds a code cave in the .text section of the DLL. If this function is unable to 
     * find a code cave at least minimalSize bytes long, it fails and so will the whole 
     * hooking attempt. By failure, will return 0.
     */
    DWORD
    FindRemoteCodeCave(HANDLE hProcess, LPVOID lpImageBaseAddress, LPCTSTR libName, SIZE_T minimalCodeCaveSize)
    {
        DWORD dwHandlerAddress;
        PLOADED_IMAGE pLoadedImage;
        PIMAGE_SECTION_HEADER pCodeSectionHeader;

        pLoadedImage =  ReadRemoteImage
        (
            hProcess,
            lpImageBaseAddress
        );

        if (pLoadedImage == NULL) {
            fprintf(stderr, "ReadRemoteImage failed...\n");
            return 0;
        }

        pCodeSectionHeader = FindSectionHeaderByName
        (
            pLoadedImage->Sections,
            pLoadedImage->NumberOfSections,
            ".text"
        );

        if (pCodeSectionHeader == NULL) {
            fprintf(stderr, "Couldn't locate the .text section. Maybe it's named differently\n");
            return 0;
        }

        /*
         * Because there is a essential difference between PE Files in memory and on disk, 
         * we might observe a phenomenon due to the different file alignment which comes handy
         * when we are in need to write our shell code to a process:
         */
        dwHandlerAddress =  (DWORD)lpImageBaseAddress + 
                            pCodeSectionHeader->VirtualAddress + 
                            pCodeSectionHeader->SizeOfRawData - minimalCodeCaveSize;

        return dwHandlerAddress;
    }

    // =============================================================================================

    BOOL
    PrintImportDirectory(HANDLE hProcess, PIMAGE_DATA_DIRECTORY imageImportDirectory, DWORD imageBase)
    {
        PCHAR buf, dllNameBuf;
        PCHAR lpFunctionNameBuf;
        PIMAGE_IMPORT_DESCRIPTOR pImageImportDescriptor;
        IMAGE_THUNK_DATA ThunkDataINT, ThunkDataIAT;
        PIMAGE_IMPORT_BY_NAME pImageImportByName;
        DWORD functionOffset, firstRVA, counter;

        firstRVA = 0;

        BOOL bSuccess = RetReadProcessMemory
        (
            &buf,
            hProcess,
            (PVOID)(imageBase + imageImportDirectory->VirtualAddress),
            50 * sizeof(IMAGE_IMPORT_DESCRIPTOR) // not more than 50 dll's in a module :)
        );

        if (!bSuccess) {
            fprintf(stderr, "RetReadProcessMemory(buf) in PrintImportDirectory() failed with %d\n", GetLastError());
            if (bSuccess != MEM_ALLOC_FAIL_CODE)
                free(&buf);
            return FALSE;
        }

        pImageImportDescriptor = (PIMAGE_IMPORT_DESCRIPTOR)buf;
        /* pImageImportDescriptor[index].Characteristics is 
         * set to 0 to indicate the end of the array of IMAGE_IMPORT_DESCRIPTORs.
         */
        while (pImageImportDescriptor->Characteristics) {

            /* Read the memory of the DLLName:) */
            bSuccess = RetReadProcessMemory
            (
                &dllNameBuf,
                hProcess,
                (PVOID)(imageBase + pImageImportDescriptor->Name),
                BUFFER_SIZE_SMALL
            );

            if (!bSuccess) {
                fprintf(stderr, "RetReadProcessMemory(dllNameBuf) in PrintImportDirectory() failed with %d\n", GetLastError());
                if (bSuccess != MEM_ALLOC_FAIL_CODE)
                    free(&dllNameBuf);
                return FALSE;
            }

            printf("\nDll \"%s\" found", (PCHAR)dllNameBuf);
            printf("\n\tOriginalFirstThunk is 0x%x", pImageImportDescriptor->OriginalFirstThunk);
            printf("\n\tFirstThunk is 0x%x", pImageImportDescriptor->FirstThunk);
            printf("\n\tTimeDateStamp is 0x%x", pImageImportDescriptor->TimeDateStamp);
            printf("\n\tForwarderChain is 0x%x", pImageImportDescriptor->ForwarderChain);

            free(&dllNameBuf);

            printf("\n\n\tFUNCTION-NAME : FUNCTION-ADDRESS : ADDRESS OF FUNCTION ADDRESS");
            functionOffset = (imageBase + pImageImportDescriptor->FirstThunk);
            counter = 0;
            while (1) {
                /* Read the memory of the INT thunk table element :) */
                bSuccess = ReadProcessMemory
                (
                    hProcess,
                    (PVOID)(imageBase + pImageImportDescriptor->OriginalFirstThunk + counter*sizeof(PVOID)),
                    &ThunkDataINT,
                    sizeof(IMAGE_THUNK_DATA),
                    NULL
                );

                if (!bSuccess) {
                    fprintf(stderr, "RetReadProcessMemory(lpThunkINTBuffer) in PrintImportDirectory() failed with %d\n", GetLastError());
                    return FALSE;
                }

                /* Read the memory of the IAT thunk table element :) */
                bSuccess = ReadProcessMemory
                (
                    hProcess,
                    (PVOID)(imageBase + pImageImportDescriptor->FirstThunk + counter*sizeof(PVOID)),
                    &ThunkDataIAT,
                    sizeof(IMAGE_THUNK_DATA),
                    NULL
                );

                if (!bSuccess) {
                    fprintf(stderr, "RetReadProcessMemory(lpThunkINTBuffer) in PrintImportDirectory() failed with %d\n", GetLastError());
                    return FALSE;
                }

                /* Check if we reached the end of the array */
                if (ThunkDataINT.u1.AddressOfData == 0 && ThunkDataIAT.u1.Function == 0)
                    break;

                if (counter == 0)
                    firstRVA = ThunkDataINT.u1.AddressOfData;

                /* 
                 * Huge problem here is that the RVA's pointing to the names of the function in the IAT
                 * are not in a ascending order. The RVA's may even be broken (yeah the linkers are bad^^)
                 * and we may get invalid indices. How can we figure out that we do have a valid RVA in  
                 * pThunkDataINT->u1.AddressOfData ?!
                 * There are just bad solutions (or lazyness when it comes to 
                 * heuristic fine tuning, so we apply a heuristic function on all RVA's of the 
                 * IMAGE_THUNK_DATA INT array to ignore RVA's which have a absolute difference from 
                 * more than 0x5000 bytes to the first RVA. What happens if the first RVA is a invalid 
                 * one? We're screwed, but at least the other is able to locate the problem quickly.
                 */
                // test if we stumbled upon a suspicious RVA (after hoping that the first is not :/)
                if (abs(ThunkDataINT.u1.AddressOfData - firstRVA) > 0x5000) {
                    fprintf(stderr, "\nRVA in INT->u1.AddressOfData might be broken (%x) - ignoring\n",
                        ThunkDataINT.u1.AddressOfData);
                } else {

                    bSuccess = RetReadProcessMemory
                    (
                        &lpFunctionNameBuf,
                        hProcess,
                        (PVOID)(imageBase + ThunkDataINT.u1.AddressOfData),
                        BUFFER_SIZE_SMALL
                    );

                    if (!bSuccess) {
                        fprintf(stderr, "RetReadProcessMemory(lpFunctionNameBuf) in HookFunction() failed with %d\n", GetLastError());
                        if (bSuccess != MEM_ALLOC_FAIL_CODE)
                            free(&lpFunctionNameBuf);
                        return FALSE;
                    }

                    pImageImportByName = (PIMAGE_IMPORT_BY_NAME)lpFunctionNameBuf;

                    printf("\n\t%s: 0x%x : 0x%x", pImageImportByName->Name,
                                    ThunkDataIAT.u1.Function, functionOffset);
                }
                functionOffset += sizeof(PVOID);
                counter++;
            }
            printf("\n\n");
            pImageImportDescriptor++;
        }

        /* We can free up now the allocated buffer */
        free(&buf);

        return TRUE;
    }

    // =============================================================================================

    /* 
     * Looks up the function address in the IAT with LibName and funcName and 
     * patches the pointer to the value in redirection. If the function succeeds, it will
     * return the OLD function pointer, so you can save it to restore the default behaviour. If 
     * HookFunction fails, it will return FALSE(0).
     */
    DWORD PatchIAT(HANDLE hProcess, PIMAGE_DATA_DIRECTORY imageImportDirectory,
         DWORD imageBase, LPCTSTR libName, LPCTSTR funcName, DWORD redirectionAddress)
    {
        PCHAR buf, dllNameBuf;
        PCHAR lpFunctionNameBuf;
        PIMAGE_IMPORT_DESCRIPTOR pImageImportDescriptor;
        IMAGE_THUNK_DATA ThunkDataINT, ThunkDataIAT;
        PIMAGE_IMPORT_BY_NAME pImageImportByName;
        DWORD functionOffset, firstRVA, counter, functionMemValue;

        firstRVA = 0;
        functionMemValue = 0;

        BOOL bSuccess = RetReadProcessMemory
        (
            &buf,
            hProcess,
            (PVOID)(imageBase + imageImportDirectory->VirtualAddress),
            50 * sizeof(IMAGE_IMPORT_DESCRIPTOR) // not more than 50 dll's in a module :)
        );

        if (!bSuccess) {
            fprintf(stderr, "RetReadProcessMemory(buf) in PrintImportDirectory() failed with %d\n", GetLastError());
            if (bSuccess != MEM_ALLOC_FAIL_CODE)
                free(&buf);
            return FALSE;
        }

        pImageImportDescriptor = (PIMAGE_IMPORT_DESCRIPTOR)buf;
        /* 
         * pImageImportDescriptor[index].Characteristics is 
         * set to 0 to indicate the end of the array of IMAGE_IMPORT_DESCRIPTORs.
         */
        while (pImageImportDescriptor->Characteristics) {

            /* Read the memory of the DLLName:) */
            bSuccess = RetReadProcessMemory
            (
                &dllNameBuf,
                hProcess,
                (PVOID)(imageBase + pImageImportDescriptor->Name),
                BUFFER_SIZE_SMALL
            );

            if (!bSuccess) {
                fprintf(stderr, "RetReadProcessMemory(dllNameBuf) in PrintImportDirectory() failed with %d\n", GetLastError());
                if (bSuccess != MEM_ALLOC_FAIL_CODE)
                    free(&dllNameBuf);
                return FALSE;
            }

            functionOffset = (imageBase + pImageImportDescriptor->FirstThunk);
            counter = 0;
            while (1) {
                /* Read the memory of the INT thunk table element :) */
                bSuccess = ReadProcessMemory
                (
                    hProcess,
                    (PVOID)(imageBase + pImageImportDescriptor->OriginalFirstThunk + counter*sizeof(PVOID)),
                    &ThunkDataINT,
                    sizeof(IMAGE_THUNK_DATA),
                    NULL
                );

                if (!bSuccess) {
                    fprintf(stderr, "RetReadProcessMemory(lpThunkINTBuffer) in PrintImportDirectory() failed with %d\n", GetLastError());
                    return FALSE;
                }

                /* Read the memory of the IAT thunk table element :) */
                bSuccess = ReadProcessMemory
                (
                    hProcess,
                    (PVOID)(imageBase + pImageImportDescriptor->FirstThunk + counter*sizeof(PVOID)),
                    &ThunkDataIAT,
                    sizeof(IMAGE_THUNK_DATA),
                    NULL
                );

                if (!bSuccess) {
                    fprintf(stderr, "RetReadProcessMemory(lpThunkINTBuffer) in PrintImportDirectory() failed with %d\n", GetLastError());
                    return FALSE;
                }

                /* Check if we reached the end of the array */
                if (ThunkDataINT.u1.AddressOfData == 0 && ThunkDataIAT.u1.Function == 0)
                    break;

                if (counter == 0)
                    firstRVA = ThunkDataINT.u1.AddressOfData;

                /* 
                 * Huge problem here is that the RVA's pointing to the names of the function in the IAT
                 * are not in a ascending order. The RVA's may even be broken (yeah the linkers are bad^^)
                 * and we may get invalid indices. How can we figure out that we do have a valid RVA in  
                 * pThunkDataINT->u1.AddressOfData ?!
                 * There are just bad solutions (or lazyness when it comes to 
                 * heuristic fine tuning, so we apply a heuristic function on all RVA's of the 
                 * IMAGE_THUNK_DATA INT array to ignore RVA's which have a absolute difference from 
                 * more than 0x5000 bytes to the first RVA. What happens if the first RVA is a invalid 
                 * one? We're screwed, but at least the other is able to locate the problem quickly.
                 */
                // test if we stumbled upon a suspicious RVA (after hoping that the first is not :/)
                if (abs(ThunkDataINT.u1.AddressOfData - firstRVA) > 0x5000) {
                    fprintf(stderr, "\nRVA in INT->u1.AddressOfData might be broken (%x) - ignoring\n",
                        ThunkDataINT.u1.AddressOfData);
                } else {

                    bSuccess = RetReadProcessMemory
                    (
                        &lpFunctionNameBuf,
                        hProcess,
                        (PVOID)(imageBase + ThunkDataINT.u1.AddressOfData),
                        BUFFER_SIZE_SMALL
                    );

                    if (!bSuccess) {
                        fprintf(stderr, "RetReadProcessMemory(lpFunctionNameBuf) in HookFunction() failed with %d\n", GetLastError());
                        if (bSuccess != MEM_ALLOC_FAIL_CODE)
                            free(&lpFunctionNameBuf);
                        return FALSE;
                    }

                    pImageImportByName = (PIMAGE_IMPORT_BY_NAME)lpFunctionNameBuf;

                    /* When we are in the whished IAT entry, we write to the process the new value of the function pointer */
                    if 
                    (
                        _stricmp(pImageImportByName->Name, funcName) == 0 &&
                        _stricmp(dllNameBuf, libName) == 0
                    ) {
                        functionMemValue = ThunkDataIAT.u1.Function; /* save because the struct will be freed up*/

                        bSuccess = RetWriteProcessMemory
                        (
                            hProcess,
                            (LPVOID)functionOffset,
                            (LPCVOID)&redirectionAddress,
                            (SIZE_T)sizeof(redirectionAddress)
                        );

                        if (!bSuccess) {
                            fprintf(stderr, "RetWriteProcessMemory() in HookFunction() failed with %d\n", GetLastError());
                            if (bSuccess != MEM_ALLOC_FAIL_CODE)
                                free(&lpFunctionNameBuf);
                            return FALSE;
                        } else {
                            fprintf(stdout, "[i] Patched the IAT API %s in DLL %s at address 0x%x :)\n",
                                                 pImageImportByName->Name, dllNameBuf, functionOffset);
                            break; /* break the while loop because we updated the IAT*/
                        }
                    }
                }
                functionOffset += sizeof(PVOID);
                counter++;
            }
            
            /* have we just been to the searched DLL? Assumes that Dll-Names in the IAT are uniqe */
            if (_stricmp(dllNameBuf, libName) == 0) {
                //free(&dllNameBuf);
                break;
            }

            pImageImportDescriptor++;
        }

        /* We can free up now the allocated buffer */
        free(&buf);

        return functionMemValue;
    }

    // =============================================================================================

    /*
     * Does the actual hooking. Finds a code cave in the .text section of the 
     * DLL which exports the function specified by funcName. It writes the handler into
     * the code cave. The sanity of the handler is not a problem of this library.
     */
    HOOK_CONTEXT *
    HookFunction(HANDLE hProcess, LPCTSTR libName, LPCTSTR funcName, PVOID handlerBuf, DWORD handlerSize)
    {
        DWORD pPEP, oldFunctionPointer, pHandler;
        SIZE_T nBytesWritten;
        PIMAGE_DATA_DIRECTORY imageImportDirectory;
        BOOL bSuccess;
        HOOK_CONTEXT *pHookContext;

        pHookContext = malloc(sizeof(HOOK_CONTEXT));

        if (pHookContext == NULL) {
            fprintf(stderr, "malloc in HookFunction() failed\n");
            return NULL;
        }

        /* Locate the Process Environment Block */
        pPEP = FindRemotePEB(hProcess);

        if (pPEP == 0) {
            fprintf(stderr, "[!] FindRemotePEB() failed...\n");
            return NULL;
        } else {
            printf("[i] Remote PEB found: 0x%x. ImageBase address is 0x%x\n",
                                 pPEP, (DWORD)((PPEB)pPEP)->ImageBaseAddress);
        }

        /* Read the RVA to the ImageImportDirectory */
        imageImportDirectory = ReadRemoteDataDirectoryRVA(hProcess,
                                    (LPCVOID)((PPEB)pPEP)->ImageBaseAddress, 1);

        if (imageImportDirectory == 0) {
            fprintf(stderr, "[!] ReadRemoteDataDirectoryRV() failed...\n");
            return NULL;
        } else {
            printf("[i] Remote Image Parsed. Virtual Address of RemoteDataDirectory: 0x%x\n",
                                                             imageImportDirectory->VirtualAddress);
        }

        /* Find a code cave where to write the handler */
        pHandler = FindRemoteCodeCave
        (
            hProcess,
            ((PPEB)pPEP)->ImageBaseAddress,
            libName,
            handlerSize
        );

        if (pHandler == 0) {
            fprintf(stderr, "[!] Cannot find code cave in remote image...\n");
            return NULL;
        } else
            printf("[i] Code cave found.\n");
        
        /* Write the shell code into the code cave :) */
        bSuccess = WriteProcessMemory
        (
            hProcess,
            (LPVOID)pHandler,
            (LPCVOID)handlerBuf,
            handlerSize,
            &nBytesWritten
        );

        if (!bSuccess) {
            fprintf(stderr, "[!] Couldn't write shell code. Wrote %d bytes instead of %d...\n",
                                                                         nBytesWritten, handlerSize);
            return NULL;
        } else
            printf("[i] Handler written to address 0x%x!\n", pHandler);


        /* Patch the IAT with a pointer to the handler */
        pHookContext->oldFuncPointer = PatchIAT
        (
            hProcess,
            imageImportDirectory,
            (DWORD)((PPEB)pPEP)->ImageBaseAddress,
            libName,
            funcName,
            (DWORD)pHandler
        );

        if (pHookContext->oldFuncPointer == 0) {
            fprintf(stderr, "[!] The specified API %s couldn't be located in the IAT\n", funcName);
            return NULL;
        }

        /* The hook should be sharp by now :) */

        //pHookContext->pOldFuncPointer = 

        return pHookContext;
    }


    BOOL
    ReleaseHook(HANDLE hProcess, HOOK_CONTEXT *pHookContext)
    {
        BOOL bSuccess;

    }

    /* 
     * Caller has to pass a pointer. Caller  has to free() then the mem allocated here
     * buf is a pointer to a pointer. Otherwise we loose the mem. This is C magic... :/ 
     */
    // =============================================================================================
    BOOL
    RetReadProcessMemory(OUT PCHAR *buf, HANDLE hProcess, LPVOID lpBaseAddress, SIZE_T sizeBuf)
    {
        BOOL bSuccess;
        DWORD oldProtect, dummy;
        SIZE_T numBytesRead;


        *buf = calloc(sizeBuf, sizeof(CHAR));

        if (buf == NULL) {
            fprintf(stderr, "calloc() in RetReadProcessMemory() failed with %d\n", GetLastError());
            return 0x666; // Little hack here
        }
        
        bSuccess = VirtualProtectEx
        (
            hProcess,
            lpBaseAddress,
            sizeBuf,
            PAGE_READONLY,
            &oldProtect
        );

        if (!bSuccess) {
            fprintf(stderr, "VirtualProtectEx() in RetReadProcessMemory() failed with %d\n", GetLastError());
            return FALSE;
        }

        /* Read finally the process memory */
        bSuccess = ReadProcessMemory
        (
            hProcess,
            lpBaseAddress,
            *buf,
            sizeBuf,
            &numBytesRead
        );

        if (!bSuccess) {
            fprintf(stderr, "ReadProcessMemory() in RetReadProcessMemory() failed with %d\n", GetLastError());
            return FALSE;
        }

        /* Restore old memory protection constants */
        bSuccess = VirtualProtectEx
        (
            hProcess,
            lpBaseAddress,
            sizeBuf,
            oldProtect,
            &dummy
        );

        if (!bSuccess) {
            fprintf(stderr, "VirtualProtectEx(RESTORING) in RetReadProcessMemory() failed with %d\n", GetLastError());
            return FALSE;
        }
        
        return TRUE;
    }

    // =============================================================================================

    BOOL
    RetWriteProcessMemory(HANDLE hProcess, LPVOID lpBaseAddress, LPCVOID lpBuffer, SIZE_T nSize)
    {
        BOOL bSuccess;
        DWORD oldProtect, dummy;
        SIZE_T numBytesWritten;

        bSuccess = VirtualProtectEx
        (
            hProcess,
            lpBaseAddress,
            nSize,
            PAGE_READWRITE,
            &oldProtect
        );

        if (!bSuccess) {
            fprintf(stderr, "VirtualProtectEx() in RetWriteProcessMemory() failed with %d\n", GetLastError());
            return FALSE;
        }

        bSuccess = WriteProcessMemory
        (
            hProcess,
            lpBaseAddress,
            lpBuffer,
            nSize,
            &numBytesWritten
        );

        if (!bSuccess) {
            fprintf(stderr, "WriteProcessMemory in WriteProcessMemory() failed with %d\n", GetLastError());
            return FALSE;
        }

        /* Restore old memory protection constants */
        bSuccess = VirtualProtectEx
        (
            hProcess,
            lpBaseAddress,
            nSize,
            oldProtect,
            &dummy
        );

        if (!bSuccess) {
            fprintf(stderr, "VirtualProtectEx(RESTORING) in RetReadProcessMemory() failed with  %d\n", GetLastError());
            return FALSE;
        }
        
        return TRUE;
    }
