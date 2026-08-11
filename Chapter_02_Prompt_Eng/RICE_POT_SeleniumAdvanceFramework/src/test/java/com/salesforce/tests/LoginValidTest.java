package com.salesforce.tests;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.Assert;
import org.testng.SkipException;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import com.salesforce.pages.LoginPage;

import io.github.bonigarcia.wdm.WebDriverManager;

public class LoginValidTest {

    private WebDriver driver;
    private LoginPage loginPage;
    private Properties config;

    @BeforeMethod
    public void setUp() {
        try {
            config = loadConfig();
            WebDriverManager.chromedriver().setup();
            driver = new ChromeDriver();
            driver.manage().window().maximize();
            driver.get(config.getProperty("salesforce.url"));
            loginPage = new LoginPage(driver);
        } catch (IOException e) {
            throw new AssertionError("Failed to load config.properties from classpath", e);
        }
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void verifyLoginPageElementsDisplayed() {
        Assert.assertTrue(loginPage.isRememberMeDisplayed(), "Remember me checkbox should be displayed");
        Assert.assertFalse(loginPage.getCurrentUrl().isEmpty(), "Login page URL should not be empty");
    }

    @Test
    public void verifyRememberMeSelection() {
        loginPage.selectRememberMe();
        Assert.assertTrue(loginPage.isRememberMeSelected(), "Remember me checkbox should be selected");
    }

    @Test
    public void testValidLoginNavigatesToHome() {
        String username = config.getProperty("salesforce.username");
        String password = config.getProperty("salesforce.password");
        if ("your-salesforce-username".equals(username) || "your-salesforce-password".equals(password)) {
            throw new SkipException("Real Salesforce credentials are not configured; skipping valid login test");
        }
        loginPage.doLogin(username, password);
        Assert.assertFalse(loginPage.getCurrentUrl().contains("login.salesforce.com"),
                "Successful login should redirect away from the Salesforce login page");
    }

    private Properties loadConfig() throws IOException {
        Properties props = new Properties();
        try (InputStream in = getClass().getClassLoader().getResourceAsStream("config.properties")) {
            if (in == null) {
                throw new IOException("config.properties not found on classpath");
            }
            props.load(in);
        }
        return props;
    }
}
