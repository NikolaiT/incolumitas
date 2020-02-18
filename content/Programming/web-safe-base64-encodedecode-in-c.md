Title: Web safe Base64 Encode/Decode in C
Date: 2012-10-29 11:21
Author: Nikolai Tschacher
Category: Programming
Tags: C, Programming
Slug: web-safe-base64-encodedecode-in-c
Status: published

A short while ago I needed to implement a little web safe base64
en/decoder and couldn't find any good small example in the width of the
internet, so I decided to do my own dirty one. I hope I help somebody
with this  little demonstration code...

I used Pelles C Compiler to build this program, but I am optimistic that
it works on every common C Compiler, since it's quite close to the C11
standard.

    :::C
    #include 
    #include 
    #include 
    #include 

    #define MAX_B64_PADDING 0x2
    #define B64_PAD_CHAR "="

    char * Base64Encode(char *input, unsigned int inputLen);
    char * Base64Decode(char *input, unsigned int inputLen);
    static unsigned char GetIndexByChar(unsigned char c);

    static char *b64alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";

    int main(int argc, char **argv) {

        if (argc != 2) {
            printf("Usage: %s StringToEncode\n", argv[0]);
            exit(EXIT_FAILURE);
        }
        printf("String \"%s\" to: " ,argv[1]);
        printf("%s\n", Base64Encode(argv[1], strlen(argv[1])));
        
        exit(EXIT_SUCCESS);
    }

    /* Caller has to free the returned base64 encoded string ! */
    char *
    Base64Encode(char *input, unsigned int inputLen)
    {
        char *encodedBuf;
        int fillBytes, i, k, base64StrLen;
        unsigned char a0, a1, a2, a3;
        /* Make sure there is no overflow. RAM is cheap :) */
        base64StrLen = inputLen + (int)(inputLen * 0.45);

        encodedBuf = calloc(base64StrLen, sizeof(char));
        if (encodedBuf == NULL) {
            printf("calloc() failed with error %d\n", errno);
            return NULL;
        }

        fillBytes = 3 - (inputLen % 3); /* Pad until dividable by 3 ! */

        k = 0;
        /* Walk in 3 byte steps*/
        for (i = 0; i < inputLen; i += 3) {

            a0 = (unsigned char)(((input[i+0] & 0xFC) >> 2));
            a1 = (unsigned char)(((input[i+0] & 0x3) << 4) + ((input[i+1] & 0xF0) >> 4));
            a2 = (unsigned char)(((input[i+1] & 0xF) << 2) + ((input[i+2] & 0xC0) >> 6));
            a3 = (unsigned char)((input[i+2] & 0x3F));

            encodedBuf[k+0] = b64alphabet[a0];
            encodedBuf[k+1] = b64alphabet[a1];
            encodedBuf[k+2] = b64alphabet[a2];
            encodedBuf[k+3] = b64alphabet[a3];
            
            /* Prevents buffer overflow */
            if (i + (3 - fillBytes) == inputLen) { /* Check if we pad */
                /* fill byte is either 0, 1 or 2 */
                switch (fillBytes) {
                    case 0: // do nothing
                        break;
                    case 1: // last encoded byte becomes pad value
                        encodedBuf[k+3] = *B64_PAD_CHAR;
                        break;
                    case 2: // last two encoded bytes become pad value
                        encodedBuf[k+2] = *B64_PAD_CHAR;
                        encodedBuf[k+3] = *B64_PAD_CHAR;
                        break;
                }
            }
            k += 4;
        }
        return encodedBuf;
    }

    /* Caller has to free the returned decoded ascii buffer */
    char * 
    Base64Decode(char *input, unsigned int inputLen)
    {
        char * decodedBuf;
        char a0, a1, a2, a3;
        int i, k, decodedLen;

        decodedLen = (int)(inputLen * 0.8); // 20 % less big than b64 encoded should be more than enough

        decodedBuf = calloc(decodedLen, sizeof(char));
        if (decodedBuf == NULL) {
            printf("calloc() failed with error %d\n", errno);
            return NULL;
        }

        k = 0;
        for (i = 0; i < inputLen; i += 4) {
            if ((i + 4) <= inputLen) {
                a0 = GetIndexByChar(input[i+0]);
                a1 = GetIndexByChar(input[i+1]);
                a2 = GetIndexByChar(input[i+2]);
                a3 = GetIndexByChar(input[i+3]);

                decodedBuf[k+0] = (char)((a0 << 2) + ((a1 & 0x30) >> 4));
                decodedBuf[k+1] = (char)(((a1 & 0xF) << 4) + ((a2 & 0x3C) >> 2));
                decodedBuf[k+2] = (char)(((a2 & 0x3) << 6) + (a3));
                
                /* Strip pad bytes. Ugly, but working solution... */
                if (a0 == 100) {
                    decodedBuf[k+0] = '\0';
                    break;
                } else if (a1 == 100) {
                    decodedBuf[k+0] = '\0';
                    break;
                } else if (a2 == 100) {
                    decodedBuf[k+1] = '\0';
                    break;
                } else if (a3 == 100) {
                    decodedBuf[k+2] = '\0';
                    break;
                }
                k += 3;
            }
        }
        return decodedBuf;
    }

    static unsigned char
    GetIndexByChar(unsigned char c)
    {
        int i;
        for (i = 0; i < 64; i++) {
            if (b64alphabet[i] == c)
                return (unsigned char)i;
        }
        return 100; /* indicates an error */
    }
