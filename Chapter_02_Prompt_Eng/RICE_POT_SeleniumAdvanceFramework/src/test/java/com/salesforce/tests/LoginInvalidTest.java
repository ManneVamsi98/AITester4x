package com.salesforce.tests;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import com.salesforce.pages.LoginPage;

import io.github.bonigarcia.wdm.WebDriverManager;

public class LoginInvalidTest {

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
    public void testLoginWithInvalidUsername() {
        loginPage.doLogin("invalid.user@example.com", "Pass@1234");
        Assert.assertTrue(loginPage.isLoginErrorDisplayed(), "Login error should be displayed for invalid username");
        Assert.assertFalse(loginPage.getLoginErrorMessage().isEmpty(), "Login error message should not be empty");
    }

    @Test
    public void testLoginWithValidUsernameInvalidPassword() {
        loginPage.doLogin(config.getProperty("salesforce.username"), "WrongPassword@1");
        Assert.assertTrue(loginPage.isLoginErrorDisplayed(), "Login error should be displayed for invalid password");
        Assert.assertFalse(loginPage.getLoginErrorMessage().isEmpty(), "Login error message should not be empty");
    }

    @Test
    public void testLoginWithBlankUsername() {
        loginPage.doLogin("", config.getProperty("salesforce.password"));
        Assert.assertTrue(loginPage.isLoginErrorDisplayed(), "Login error should be displayed for blank username");
        Assert.assertFalse(loginPage.getLoginErrorMessage().isEmpty(), "Login error message should not be empty");
    }

    @Test
    public void testLoginWithBlankPassword() {
        loginPage.doLogin(config.getProperty("salesforce.username"), "");
        Assert.assertTrue(loginPage.isLoginErrorDisplayed(), "Login error should be displayed for blank password");
        Assert.assertFalse(loginPage.getLoginErrorMessage().isEmpty(), "Login error message should not be empty");
    }

    @Test
    public void testLoginWithBothFieldsBlank() {
        loginPage.doLogin("", "");
        Assert.assertTrue(loginPage.isLoginErrorDisplayed(), "Login error should be displayed for blank credentials");
        Assert.assertFalse(loginPage.getLoginErrorMessage().isEmpty(), "Login error message should not be empty");
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
