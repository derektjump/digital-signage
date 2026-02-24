package ca.jump.thegrid.signage;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.widget.LinearLayout;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.ProgressBar;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * MainActivity for The Grid Fire TV Signage App
 *
 * This activity manages the registration flow and content playback for
 * digital signage on Fire TV devices.
 *
 * Flow:
 * 1. Request registration code from API
 * 2. Display code to user for entry in admin panel
 * 3. Poll API until device is registered and has content assigned
 * 4. Transition to playback mode (WebView)
 * 5. If playlist, rotate through screens; if single screen, display it
 */
public class MainActivity extends Activity {

    // API Configuration
    private static final String API_BASE_URL = "https://digital-signage-g7atd8ehcnazdafb.canadaeast-01.azurewebsites.net";
    private static final String REQUEST_CODE_ENDPOINT = "/api/devices/request-code/";
    private static final String CONFIG_ENDPOINT = "/api/devices/%s/config/";

    // Registration polling interval (check every 5 seconds)
    private static final long POLL_INTERVAL_MS = 5000;

    // Content polling interval (check every 10 seconds during playback)
    private static final long CONTENT_POLL_INTERVAL_MS = 10000;

    // SharedPreferences for persistent storage
    private static final String PREFS_NAME = "GridSignagePrefs";
    private static final String PREF_DEVICE_ID = "device_id";
    private static final String PREF_AUTO_LAUNCH_ON_BOOT = "auto_launch_on_boot";
    private static final String PREF_AUTO_RELAUNCH_ON_EXIT = "auto_relaunch_on_exit";

    // Cheat code sequence: UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT
    // On Fire TV remote: DPAD_UP, DPAD_UP, DPAD_DOWN, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT, DPAD_LEFT, DPAD_RIGHT
    private static final int[] CHEAT_CODE = {
            KeyEvent.KEYCODE_DPAD_UP,
            KeyEvent.KEYCODE_DPAD_UP,
            KeyEvent.KEYCODE_DPAD_DOWN,
            KeyEvent.KEYCODE_DPAD_DOWN,
            KeyEvent.KEYCODE_DPAD_LEFT,
            KeyEvent.KEYCODE_DPAD_RIGHT,
            KeyEvent.KEYCODE_DPAD_LEFT,
            KeyEvent.KEYCODE_DPAD_RIGHT
    };
    private int cheatCodeIndex = 0;
    private long lastKeyTime = 0;
    private static final long CHEAT_CODE_TIMEOUT_MS = 5000; // Reset sequence after 5 seconds of inactivity

    // Playlist rotation handler
    private Handler playlistHandler;
    private int currentPlaylistIndex = 0;
    private List<PlaylistItem> playlistItems;

    // HTTP client
    private OkHttpClient httpClient;

    // Device registration data
    private String deviceId;
    private String registrationCode;

    // Current content tracking (for detecting changes)
    private String currentContentType = "none";
    private String currentContentId = null;
    private int currentPlaylistItemCount = 0;  // Track playlist item count for change detection

    // UI Components
    private View registrationLayout;
    private TextView codeLabelTextView;
    private TextView codeTextView;
    private TextView statusTextView;
    private ProgressBar progressBar;
    private WebView webView;

    // Handlers
    private Handler pollHandler;
    private Runnable pollRunnable;

    // Wake lock to prevent device sleep
    private PowerManager.WakeLock wakeLock;

    // Settings dialog state
    private boolean isSettingsOpen = false;
    private boolean isUserExiting = false; // Track if user intentionally exited via settings

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Keep screen on and prevent sleep/screensaver
        getWindow().addFlags(
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON |
                WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD |
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED |
                WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
        );

        // Acquire wake lock to prevent CPU sleep
        PowerManager powerManager = (PowerManager) getSystemService(Context.POWER_SERVICE);
        wakeLock = powerManager.newWakeLock(
                PowerManager.FULL_WAKE_LOCK | PowerManager.ACQUIRE_CAUSES_WAKEUP,
                "TheGrid:SignageWakeLock"
        );
        wakeLock.acquire();

        // Initialize HTTP client with timeouts
        httpClient = new OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(10, TimeUnit.SECONDS)
                .writeTimeout(10, TimeUnit.SECONDS)
                .build();

        // Initialize UI components
        registrationLayout = findViewById(R.id.registration_layout);
        codeLabelTextView = findViewById(R.id.code_label);
        codeTextView = findViewById(R.id.code_text);
        statusTextView = findViewById(R.id.status_text);
        progressBar = findViewById(R.id.progress_bar);
        webView = findViewById(R.id.webview);

        // Configure WebView for full-screen signage
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setLoadWithOverviewMode(true);
        webSettings.setUseWideViewPort(true);
        webSettings.setCacheMode(WebSettings.LOAD_NO_CACHE);

        // WebView client to handle page loads
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                // Hide system UI for true full-screen
                hideSystemUI();
            }
        });

        // Initialize handlers
        pollHandler = new Handler(Looper.getMainLooper());
        playlistHandler = new Handler(Looper.getMainLooper());

        // Check for saved device ID first
        String savedDeviceId = loadSavedDeviceId();
        if (savedDeviceId != null) {
            // Device was previously registered - skip registration, go straight to polling
            deviceId = savedDeviceId;
            updateStatus("Reconnecting to The Grid...");
            startPollingForConfig();
        } else {
            // New device - start registration flow
            requestRegistrationCode();
        }
    }

    /**
     * Request a registration code from the API
     */
    private void requestRegistrationCode() {
        updateStatus("Requesting registration code...");

        String url = API_BASE_URL + REQUEST_CODE_ENDPOINT;
        JSONObject requestBody = new JSONObject();

        try {
            requestBody.put("device_name", "Fire TV Device");
        } catch (JSONException e) {
            e.printStackTrace();
        }

        RequestBody body = RequestBody.create(
                requestBody.toString(),
                MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                runOnUiThread(() -> {
                    updateStatus("Error connecting to server. Retrying...");
                    // Retry after 3 seconds
                    new Handler(Looper.getMainLooper()).postDelayed(
                            MainActivity.this::requestRegistrationCode,
                            3000
                    );
                });
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    try {
                        JSONObject json = new JSONObject(response.body().string());
                        if (json.getBoolean("success")) {
                            deviceId = json.getString("device_id");
                            registrationCode = json.getString("registration_code");

                            // Save device ID for persistence across restarts
                            saveDeviceId(deviceId);

                            runOnUiThread(() -> {
                                displayRegistrationCode();
                                startPollingForConfig();
                            });
                        } else {
                            throw new Exception("API returned success=false");
                        }
                    } catch (Exception e) {
                        runOnUiThread(() -> {
                            updateStatus("Error parsing response. Retrying...");
                            new Handler(Looper.getMainLooper()).postDelayed(
                                    MainActivity.this::requestRegistrationCode,
                                    3000
                            );
                        });
                    }
                } else {
                    runOnUiThread(() -> {
                        updateStatus("Server error. Retrying...");
                        new Handler(Looper.getMainLooper()).postDelayed(
                                MainActivity.this::requestRegistrationCode,
                                3000
                        );
                    });
                }
            }
        });
    }

    /**
     * Display the registration code on screen
     */
    private void displayRegistrationCode() {
        codeLabelTextView.setVisibility(View.VISIBLE);  // Show "Registration Code:" label
        codeTextView.setText(registrationCode);
        codeTextView.setTextSize(72);  // Reset to normal size
        updateStatus("Enter this code in The Grid admin panel to assign content");
        progressBar.setVisibility(View.VISIBLE);
    }

    /**
     * Start polling the API for device configuration
     */
    private void startPollingForConfig() {
        pollRunnable = new Runnable() {
            @Override
            public void run() {
                checkDeviceConfig();
                pollHandler.postDelayed(this, POLL_INTERVAL_MS);
            }
        };
        pollHandler.post(pollRunnable);
    }

    /**
     * Check if device has been configured with content
     */
    private void checkDeviceConfig() {
        String url = API_BASE_URL + String.format(CONFIG_ENDPOINT, deviceId);

        Request request = new Request.Builder()
                .url(url)
                .get()
                .build();

        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                // Silently fail, will retry on next poll
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                // Handle 404 - device was deleted from server
                if (response.code() == 404) {
                    runOnUiThread(() -> {
                        // Clear saved device ID and restart registration
                        clearSavedDeviceId();
                        pollHandler.removeCallbacks(pollRunnable);
                        registrationLayout.setVisibility(View.VISIBLE);
                        webView.setVisibility(View.GONE);
                        currentContentType = "none";
                        currentContentId = null;
                        currentPlaylistItemCount = 0;
                        requestRegistrationCode();
                    });
                    return;
                }

                if (response.isSuccessful()) {
                    try {
                        JSONObject json = new JSONObject(response.body().string());
                        if (json.getBoolean("success") && json.getBoolean("registered")) {
                            JSONObject config = json.getJSONObject("config");
                            String configType = config.getString("type");

                            // Get content ID and item count for change detection
                            String contentId = null;
                            int playlistItemCount = 0;
                            if (configType.equals("playlist")) {
                                contentId = config.getString("playlist_id");
                                JSONArray items = config.getJSONArray("items");
                                playlistItemCount = items.length();
                            } else if (configType.equals("screen")) {
                                contentId = config.getString("screen_id");
                            }

                            // Handle "none" type - device registered but no content assigned
                            if (configType.equals("none")) {
                                // Reset tracking so we detect when content is assigned
                                currentContentType = "none";
                                currentContentId = null;
                                currentPlaylistItemCount = 0;
                                runOnUiThread(() -> showWaitingForContent());
                                return;
                            }

                            // Check if content has changed (including playlist item count changes)
                            final int finalPlaylistItemCount = playlistItemCount;
                            boolean contentChanged = !configType.equals(currentContentType) ||
                                    (contentId != null && !contentId.equals(currentContentId)) ||
                                    (configType.equals("playlist") && playlistItemCount != currentPlaylistItemCount);

                            if (contentChanged) {
                                // Update tracking
                                currentContentType = configType;
                                currentContentId = contentId;
                                currentPlaylistItemCount = finalPlaylistItemCount;

                                // Switch to content polling interval
                                pollHandler.removeCallbacks(pollRunnable);
                                pollRunnable = new Runnable() {
                                    @Override
                                    public void run() {
                                        checkDeviceConfig();
                                        pollHandler.postDelayed(this, CONTENT_POLL_INTERVAL_MS);
                                    }
                                };
                                pollHandler.postDelayed(pollRunnable, CONTENT_POLL_INTERVAL_MS);

                                // Start/restart playback
                                runOnUiThread(() -> startPlayback(config, configType));
                            }
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            }
        });
    }

    /**
     * Show "waiting for content" message when device is registered but no content assigned
     */
    private void showWaitingForContent() {
        registrationLayout.setVisibility(View.VISIBLE);
        webView.setVisibility(View.GONE);
        codeLabelTextView.setVisibility(View.GONE);  // Hide "Registration Code:" label
        codeTextView.setText("✓");
        codeTextView.setTextSize(48);  // Smaller checkmark
        updateStatus("Device registered!\n\nWaiting for content to be assigned in The Grid admin panel...");
        progressBar.setVisibility(View.VISIBLE);
    }

    /**
     * Start content playback based on configuration
     */
    private void startPlayback(JSONObject config, String configType) {
        try {
            if (configType.equals("playlist")) {
                // Playlist mode - load items and start rotation
                JSONArray items = config.getJSONArray("items");
                playlistItems = new ArrayList<>();

                for (int i = 0; i < items.length(); i++) {
                    JSONObject item = items.getJSONObject(i);
                    playlistItems.add(new PlaylistItem(
                            item.getString("player_url"),
                            item.getInt("duration_seconds")
                    ));
                }

                if (playlistItems.isEmpty()) {
                    // Playlist has no screens - show waiting message
                    // Reset item count to 0 so we detect when screens are added
                    currentPlaylistItemCount = 0;
                    showWaitingForContent();
                    updateStatus("Playlist assigned but contains no screens.\n\nAdd screens to the playlist in The Grid admin panel.");
                    return;
                }

                // Stop any existing playlist rotation
                playlistHandler.removeCallbacksAndMessages(null);

                // Hide registration UI, show WebView
                registrationLayout.setVisibility(View.GONE);
                webView.setVisibility(View.VISIBLE);

                // Start playlist rotation
                currentPlaylistIndex = 0;
                loadPlaylistItem(0);

            } else if (configType.equals("screen")) {
                // Single screen mode - load and display
                String playerUrl = config.getString("player_url");

                // Stop any existing playlist rotation
                playlistHandler.removeCallbacksAndMessages(null);

                // Hide registration UI, show WebView
                registrationLayout.setVisibility(View.GONE);
                webView.setVisibility(View.VISIBLE);

                // Load screen
                webView.loadUrl(playerUrl);
            }
        } catch (JSONException e) {
            e.printStackTrace();
            updateStatus("Error loading content configuration");
        }
    }

    /**
     * Load a specific playlist item
     */
    private void loadPlaylistItem(int index) {
        if (playlistItems == null || playlistItems.isEmpty()) {
            return;
        }

        PlaylistItem item = playlistItems.get(index);
        webView.loadUrl(item.url);

        // Schedule next item
        playlistHandler.postDelayed(() -> {
            currentPlaylistIndex = (currentPlaylistIndex + 1) % playlistItems.size();
            loadPlaylistItem(currentPlaylistIndex);
        }, item.durationSeconds * 1000L);
    }

    /**
     * Update status text
     */
    private void updateStatus(String message) {
        statusTextView.setText(message);
    }

    /**
     * Hide system UI for true full-screen mode
     */
    private void hideSystemUI() {
        View decorView = getWindow().getDecorView();
        decorView.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                        | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_FULLSCREEN
        );
    }

    /**
     * Save device ID to persistent storage
     */
    private void saveDeviceId(String id) {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        prefs.edit().putString(PREF_DEVICE_ID, id).apply();
    }

    /**
     * Load saved device ID from persistent storage
     * @return device ID or null if not saved
     */
    private String loadSavedDeviceId() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        return prefs.getString(PREF_DEVICE_ID, null);
    }

    /**
     * Clear saved device ID (used when device is deleted from server)
     */
    private void clearSavedDeviceId() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        prefs.edit().remove(PREF_DEVICE_ID).apply();
        deviceId = null;
        registrationCode = null;
    }

    @Override
    protected void onResume() {
        super.onResume();
        hideSystemUI();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Clean up handlers
        if (pollHandler != null && pollRunnable != null) {
            pollHandler.removeCallbacks(pollRunnable);
        }
        if (playlistHandler != null) {
            playlistHandler.removeCallbacksAndMessages(null);
        }
        // Release wake lock
        if (wakeLock != null && wakeLock.isHeld()) {
            wakeLock.release();
        }

        // Auto-relaunch if enabled and user didn't intentionally exit
        if (!isUserExiting && isAutoRelaunchEnabled()) {
            Intent restartIntent = new Intent(this, MainActivity.class);
            restartIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            startActivity(restartIntent);
        }
    }

    @Override
    public void onBackPressed() {
        // If auto-relaunch is enabled, don't allow back button to exit
        if (isAutoRelaunchEnabled() && !isSettingsOpen) {
            Toast.makeText(this, "Exit disabled. Use settings to exit.", Toast.LENGTH_SHORT).show();
            return;
        }
        super.onBackPressed();
    }

    /**
     * Handle key events for cheat code detection
     * Using dispatchKeyEvent to catch keys even when WebView has focus
     */
    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        // Only process key down events
        if (event.getAction() == KeyEvent.ACTION_DOWN) {
            int keyCode = event.getKeyCode();

            // Don't process cheat code if settings dialog is open
            if (!isSettingsOpen) {
                long currentTime = System.currentTimeMillis();

                // Reset sequence if too much time has passed
                if (currentTime - lastKeyTime > CHEAT_CODE_TIMEOUT_MS) {
                    cheatCodeIndex = 0;
                }
                lastKeyTime = currentTime;

                // Only process d-pad keys for cheat code
                if (keyCode == KeyEvent.KEYCODE_DPAD_UP ||
                    keyCode == KeyEvent.KEYCODE_DPAD_DOWN ||
                    keyCode == KeyEvent.KEYCODE_DPAD_LEFT ||
                    keyCode == KeyEvent.KEYCODE_DPAD_RIGHT) {

                    // Check if this key matches the next expected key in sequence
                    if (keyCode == CHEAT_CODE[cheatCodeIndex]) {
                        cheatCodeIndex++;

                        // Check if entire sequence is complete
                        if (cheatCodeIndex == CHEAT_CODE.length) {
                            cheatCodeIndex = 0;
                            showSettingsDialog();
                            return true;
                        }
                    } else {
                        // Wrong key - reset and check if it starts a new sequence
                        if (keyCode == CHEAT_CODE[0]) {
                            cheatCodeIndex = 1;
                        } else {
                            cheatCodeIndex = 0;
                        }
                    }
                }
                // Non-directional keys don't affect the sequence
            }
        }

        return super.dispatchKeyEvent(event);
    }

    /**
     * Show the hidden settings dialog
     */
    private void showSettingsDialog() {
        isSettingsOpen = true;

        // Load current settings
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        boolean autoLaunchOnBoot = prefs.getBoolean(PREF_AUTO_LAUNCH_ON_BOOT, true);
        boolean autoRelaunchOnExit = prefs.getBoolean(PREF_AUTO_RELAUNCH_ON_EXIT, true);

        // Create dialog layout
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(50, 30, 50, 30);
        layout.setBackgroundColor(0xFF111216);

        // Title
        TextView title = new TextView(this);
        title.setText("THE GRID - Settings");
        title.setTextSize(24);
        title.setTextColor(0xFF6434F8);
        title.setPadding(0, 0, 0, 30);
        layout.addView(title);

        // Device ID display
        TextView deviceIdLabel = new TextView(this);
        deviceIdLabel.setText("Device ID:");
        deviceIdLabel.setTextSize(14);
        deviceIdLabel.setTextColor(0x99FFFFFF);
        layout.addView(deviceIdLabel);

        TextView deviceIdValue = new TextView(this);
        deviceIdValue.setText(deviceId != null ? deviceId : "Not registered");
        deviceIdValue.setTextSize(12);
        deviceIdValue.setTextColor(0xFF00F0FF);
        deviceIdValue.setPadding(0, 0, 0, 30);
        layout.addView(deviceIdValue);

        // Auto-launch on boot toggle
        LinearLayout bootRow = new LinearLayout(this);
        bootRow.setOrientation(LinearLayout.HORIZONTAL);
        bootRow.setPadding(16, 20, 16, 20);
        bootRow.setGravity(android.view.Gravity.CENTER_VERTICAL);
        bootRow.setFocusable(true);
        bootRow.setBackground(createFocusableRowBackground());

        TextView bootLabel = new TextView(this);
        bootLabel.setText("Auto-launch on boot");
        bootLabel.setTextSize(16);
        bootLabel.setTextColor(0xFFFFFFFF);
        bootLabel.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        bootRow.addView(bootLabel);

        Switch bootSwitch = new Switch(this);
        bootSwitch.setChecked(autoLaunchOnBoot);
        styleSwitchForVisibility(bootSwitch);
        bootSwitch.setOnCheckedChangeListener((buttonView, isChecked) -> {
            prefs.edit().putBoolean(PREF_AUTO_LAUNCH_ON_BOOT, isChecked).apply();
        });
        bootRow.addView(bootSwitch);

        // Allow clicking the row to toggle the switch
        bootRow.setOnClickListener(v -> bootSwitch.toggle());
        layout.addView(bootRow);

        // Auto-relaunch on exit toggle
        LinearLayout relaunchRow = new LinearLayout(this);
        relaunchRow.setOrientation(LinearLayout.HORIZONTAL);
        relaunchRow.setPadding(16, 20, 16, 20);
        relaunchRow.setGravity(android.view.Gravity.CENTER_VERTICAL);
        relaunchRow.setFocusable(true);
        relaunchRow.setBackground(createFocusableRowBackground());

        TextView relaunchLabel = new TextView(this);
        relaunchLabel.setText("Auto-relaunch when closed");
        relaunchLabel.setTextSize(16);
        relaunchLabel.setTextColor(0xFFFFFFFF);
        relaunchLabel.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        relaunchRow.addView(relaunchLabel);

        Switch relaunchSwitch = new Switch(this);
        relaunchSwitch.setChecked(autoRelaunchOnExit);
        styleSwitchForVisibility(relaunchSwitch);
        relaunchSwitch.setOnCheckedChangeListener((buttonView, isChecked) -> {
            prefs.edit().putBoolean(PREF_AUTO_RELAUNCH_ON_EXIT, isChecked).apply();
        });
        relaunchRow.addView(relaunchSwitch);

        // Allow clicking the row to toggle the switch
        relaunchRow.setOnClickListener(v -> relaunchSwitch.toggle());
        layout.addView(relaunchRow);

        // Hint text
        TextView hint = new TextView(this);
        hint.setText("\nCheat code: ↑↑↓↓←→←→");
        hint.setTextSize(12);
        hint.setTextColor(0x66FFFFFF);
        hint.setPadding(0, 30, 0, 0);
        layout.addView(hint);

        // Build dialog
        AlertDialog.Builder builder = new AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert);
        builder.setView(layout);
        builder.setCancelable(true);

        // Reset device button
        builder.setNeutralButton("Reset Device", (dialog, which) -> {
            new AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
                    .setTitle("Reset Device?")
                    .setMessage("This will clear the device registration and restart the setup process.")
                    .setPositiveButton("Reset", (d, w) -> {
                        clearSavedDeviceId();
                        isSettingsOpen = false;
                        // Restart activity
                        Intent intent = getIntent();
                        finish();
                        startActivity(intent);
                    })
                    .setNegativeButton("Cancel", (d, w) -> {
                        isSettingsOpen = false;
                    })
                    .show();
        });

        // Exit app button
        builder.setNegativeButton("Exit App", (dialog, which) -> {
            isUserExiting = true;
            isSettingsOpen = false;
            finish();
        });

        // Close button
        builder.setPositiveButton("Close", (dialog, which) -> {
            isSettingsOpen = false;
        });

        AlertDialog dialog = builder.create();
        dialog.setOnDismissListener(d -> isSettingsOpen = false);
        dialog.show();
    }

    /**
     * Check if auto-launch on boot is enabled
     */
    public boolean isAutoLaunchEnabled() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        return prefs.getBoolean(PREF_AUTO_LAUNCH_ON_BOOT, true); // Default to enabled
    }

    /**
     * Check if auto-relaunch on exit is enabled
     */
    public boolean isAutoRelaunchEnabled() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        return prefs.getBoolean(PREF_AUTO_RELAUNCH_ON_EXIT, true); // Default to enabled
    }

    /**
     * Create a background drawable that highlights when focused (for D-pad navigation)
     */
    private StateListDrawable createFocusableRowBackground() {
        StateListDrawable stateList = new StateListDrawable();

        // Focused state - bright purple border
        GradientDrawable focused = new GradientDrawable();
        focused.setCornerRadius(8);
        focused.setColor(0xFF1a1d24);
        focused.setStroke(3, 0xFF6434F8);

        // Normal state - transparent
        GradientDrawable normal = new GradientDrawable();
        normal.setCornerRadius(8);
        normal.setColor(0x00000000);

        stateList.addState(new int[]{android.R.attr.state_focused}, focused);
        stateList.addState(new int[]{}, normal);

        return stateList;
    }

    /**
     * Style a Switch for better visibility - brighter thumb when OFF
     */
    private void styleSwitchForVisibility(Switch switchView) {
        // Create thumb colors: when OFF use a visible gray, when ON use purple
        int[][] thumbStates = new int[][] {
            new int[] { android.R.attr.state_checked },  // ON
            new int[] { }                                 // OFF
        };
        int[] thumbColors = new int[] {
            0xFF6434F8,  // ON - purple
            0xFFBBBBBB   // OFF - light gray (more visible)
        };
        switchView.setThumbTintList(new ColorStateList(thumbStates, thumbColors));

        // Create track colors: darker versions
        int[][] trackStates = new int[][] {
            new int[] { android.R.attr.state_checked },  // ON
            new int[] { }                                 // OFF
        };
        int[] trackColors = new int[] {
            0xFF4a24b8,  // ON - darker purple
            0xFF555555   // OFF - medium gray (visible track)
        };
        switchView.setTrackTintList(new ColorStateList(trackStates, trackColors));
    }

    /**
     * Simple data class for playlist items
     */
    private static class PlaylistItem {
        String url;
        int durationSeconds;

        PlaylistItem(String url, int durationSeconds) {
            this.url = url;
            this.durationSeconds = durationSeconds;
        }
    }
}
