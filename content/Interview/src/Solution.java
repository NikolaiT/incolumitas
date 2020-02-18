import java.util.HashMap;

class Solution {

    static HashMap<String, Boolean> hmap = new HashMap<String, Boolean>();
    
    public static Boolean isPalindrome(String substr) {
        
        if (!hmap.containsKey(substr)) {
            int n = substr.length();
            if (n <= 1) {
                return true;
            }
            hmap.put(substr, substr.charAt(0) == substr.charAt(n-1) && isPalindrome(substr.substring(1, n-1)));
        }
        return hmap.get(substr);
    }
    
    public String longestPalindrome(String s) {
        
        if (s.length() <= 1) {
            return s;
        }
        
        int max = 0;
        String longest = "";
        
        for (int i = 0; i < s.length(); i++) {
            for (int j = i; j < s.length(); j++) {
                if (isPalindrome(s.substring(i, j+1))) {
                    if (max <= j-i) {
                        max = j-i;
                        longest = s.substring(i, j+1);
                    }
                }
            }
        }
        return longest;
    }
    
    public static void main(String[] args) {
        Solution sol = new Solution();
        System.out.println("Longest Palindrome is: " + sol.longestPalindrome("civilwartestingwhetherthatnaptionoranynartionsoconceivedandsodedicatedcanlongendureWeareqmetonagreatbattlefiemldoftzhatwarWehavecometodedicpateaportionofthatfieldasafinalrestingplaceforthosewhoheregavetheirlivesthatthatnationmightliveItisaltogetherfangandproperthatweshoulddothisButinalargersensewecannotdedicatewecannotconsecratewecannothallowthisgroundThebravelmenlivinganddeadwhostruggledherehaveconsecrateditfaraboveourpoorponwertoaddordetractTgheworldadswfilllittlenotlenorlongrememberwhatwesayherebutitcanneverforgetwhattheydidhereItisforusthelivingrathertobededicatedheretotheulnfinishedworkwhichtheywhofoughtherehavethusfarsonoblyadvancedItisratherforustobeherededicatedtothegreattdafskremainingbeforeusthatfromthesehonoreddeadwetakeincreaseddevotiontothatcauseforwhichtheygavethelastpfullmeasureofdevotionthatweherehighlyresolvethatthesedeadshallnothavediedinvainthatthisnationunsderGodshallhaveanewbirthoffreedomandthatgovernmentofthepeoplebythepeopleforthepeopleshallnotperishfromtheearth"));
    }
}
