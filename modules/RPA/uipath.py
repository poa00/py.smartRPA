# ******************************
# UiPath
# Automatically generate RPA script compatible with UiPath. Called by
# GUI when main process is terminated and csv is available.
# ******************************
import sys

sys.path.append('../')  # this way main file is visible from this file
import os
import re
from lxml import etree
import uuid
import pandas
from multiprocessing.queues import Queue
from distutils.dir_util import copy_tree
import string
import utils
import modules
import ntpath
import difflib


class UIPathXAML:

    def __init__(self, csv_file_path: str, status_queue: Queue):
        self.csv_file_path = csv_file_path
        self.status_queue = status_queue
        self.RPA_directory = utils.utils.getRPADirectory(self.csv_file_path)
        self.UiPath_directory = os.path.join(self.RPA_directory, utils.utils.SW_ROBOT_FOLDER, 'UiPath')
        # xaml attributes
        self.root = None
        self.sequence_id = 0
        self.typeInto_id = 0
        self.click_id = 0
        self.setToClipboard = 0
        self.browserScope = 0
        self.sendHotkey = 0
        self.navigateTo = 0
        self.comment = 0
        self.openApplication = 0
        self.excelApplication = 0
        self.writeCell = 0
        self.closeTab = 0
        self.saveWorkbook = 0
        self.closeWorkbook = 0
        self.closeApplication = 0
        self.startProcess = 0
        self.createFile = 0
        self.createDirectory = 0
        self.moveFile = 0
        self.powerpointApplicationCard = 0
        self.insertSlide = 0

    # base
    def __createRoot(self):  # https://stackoverflow.com/a/31074030
        self.xmlns = "http://schemas.microsoft.com/netfx/2009/xaml/activities"
        self.mc = "http://schemas.openxmlformats.org/markup-compatibility/2006"
        self.mva = "clr-namespace:Microsoft.VisualBasic.Activities;assembly=System.Activities"
        self.sap = "http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation"
        self.sap2010 = "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation"
        self.scg = "clr-namespace:System.Collections.Generic;assembly=mscorlib"
        self.sco = "clr-namespace:System.Collections.ObjectModel;assembly=mscorlib"
        self.x = "http://schemas.microsoft.com/winfx/2006/xaml"
        self.ui = "http://schemas.uipath.com/workflow/activities"
        self.upab = "clr-namespace:UiPath.PowerPoint.Activities.Business;assembly=UiPath.PowerPoint.Activities"
        self.upadb = "clr-namespace:UiPath.PowerPoint.Activities.Design.Business;assembly=UiPath.PowerPoint.Activities"

        etree.register_namespace("mc", self.mc)
        etree.register_namespace("mva", self.mva)
        etree.register_namespace("sap", self.sap)
        etree.register_namespace("sap2010", self.sap2010)
        etree.register_namespace("scg", self.scg)
        etree.register_namespace("sco", self.sco)
        etree.register_namespace("x", self.x)
        etree.register_namespace("ui", self.ui)
        etree.register_namespace("upab", self.upab)
        etree.register_namespace("upadb", self.upadb)

        nsmap = {
            None: self.xmlns,
            "mc": self.mc,
            "mva": self.mva,
            "sap": self.sap,
            "sap2010": self.sap2010,
            "scg": self.scg,
            "x": self.x,
            "ui": self.ui,
            "upab": self.upab,
            "upadb": self.upadb,
        }

        qnames = {
            etree.QName(self.x, "Class"): "Main",
            etree.QName(self.sap2010, "WorkflowViewState.IdRef"): "ActivityBuilder_1",
            etree.QName(self.mc, "Ignorable"): "sap sap2010",
            etree.QName(self.mva, "VisualBasic.Settings"): "{x:Null}",
        }

        self.root = etree.Element(
            etree.QName(self.xmlns, "Activity"),
            qnames,
            nsmap=nsmap
        )

    def __createTextExpression(self):
        textExpression = etree.Element('TextExpression.NamespacesForImplementation')
        collection = etree.Element(
            etree.QName(self.sco, "Collection"),
            {etree.QName(self.x, "TypeArguments"): "x:String"},
        )
        props = ["System.Activities", "System.Activities.Statements", "System.Activities.Expressions",
                 "System.Activities.Validation", "System.Activities.XamlIntegration", "Microsoft.VisualBasic",
                 "Microsoft.VisualBasic.Activities", "System", "System.Collections", "System.Collections.Generic",
                 "System.Data", "System.Diagnostics", "System.Drawing", "System.IO", "System.Linq", "System.Net.Mail",
                 "System.Xml", "System.Xml.Linq", "UiPath.Core", "UiPath.Core.Activities", "System.Windows.Markup",
                 "UiPath.Excel", "UiPath.PowerPoint.Activities", "UiPath.CV"]
        for text in props:
            s = etree.Element(etree.QName(self.x, "String"))
            s.text = text
            collection.append(s)
        textExpression.append(collection)
        self.root.append(textExpression)

        textExpression = etree.Element('TextExpression.ReferencesForImplementation')
        collection = etree.Element(
            etree.QName(self.sco, "Collection"),
            {etree.QName(self.x, "TypeArguments"): "AssemblyReference"},
        )
        props = ["System.Activities", "Microsoft.VisualBasic", "mscorlib", "System.Data", "System", "System.Drawing",
                 "System.Core", "System.Xml", "System.Xml.Linq", "PresentationFramework", "WindowsBase",
                 "PresentationCore", "System.Xaml", "UiPath.System.Activities", "UiPath.UiAutomation.Activities",
                 "UiPath.System.Activities.Design", "System.ValueTuple", "System.ServiceModel", "UiPath.Excel",
                 "UiPath.CV", "UiPath.PowerPoint.Activities"]
        for text in props:
            s = etree.Element("AssemblyReference")
            s.text = text
            collection.append(s)
        textExpression.append(collection)
        self.root.append(textExpression)

    def __createMainSequence(self):
        self.sequence_id += 1
        self.mainSequence = etree.Element(
            etree.QName(None, "Sequence"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Sequence_{self.sequence_id}",
                etree.QName(None, "DisplayName"): "MainSequence"
            },
        )
        variables = etree.Element("Sequence.Variables")
        variables.extend([
            etree.Element(
                etree.QName(None, "Variable"),
                {
                    etree.QName(self.x, "TypeArguments"): "ui:Browser",
                    etree.QName(None, "Name"): "browserReference"
                },
            ),
            etree.Element(
                etree.QName(None, "Variable"),
                {
                    etree.QName(self.x, "TypeArguments"): "ui:WorkbookApplication",
                    etree.QName(None, "Name"): "spreadsheetReference"
                },
            ),
            # etree.Element(
            #     etree.QName(None, "Variable"),
            #     {
            #         etree.QName(self.x, "TypeArguments"): "x:String",
            #         etree.QName(None, "Name"): "currentUrl"
            #     },
            # ),
            # etree.Element(
            #     etree.QName(None, "Variable"),
            #     {
            #         etree.QName(self.x, "TypeArguments"): "ui:IPresentationQuickHandle",
            #         etree.QName(None, "Name"): "powerpointReference"
            #     },
            # )
        ])
        state = etree.Element(etree.QName(self.sap, "WorkflowViewStateService.ViewState"))
        dictionary = etree.Element(
            etree.QName(self.scg, "Dictionary"),
            {etree.QName(self.x, "TypeArguments"): "x:String, x:Object"},
        )
        boolean = etree.Element(
            etree.QName(self.x, "Boolean"),
            {etree.QName(self.x, "Key"): "IsExpanded"},
        )
        boolean.text = "True"

        dictionary.append(boolean)
        state.append(dictionary)
        self.mainSequence.append(variables)
        self.mainSequence.append(state)
        self.root.append(self.mainSequence)

    def __createSequence(self, children: list, displayName: str = "Do"):
        self.sequence_id += 1
        sequence = etree.Element(
            etree.QName(None, "Sequence"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Sequence_{self.sequence_id}",
                etree.QName(None, "DisplayName"): displayName
            },
        )
        state = etree.Element(etree.QName(self.sap, "WorkflowViewStateService.ViewState"))
        dictionary = etree.Element(
            etree.QName(self.scg, "Dictionary"),
            {etree.QName(self.x, "TypeArguments"): "x:String, x:Object"},
        )
        boolean = etree.Element(
            etree.QName(self.x, "Boolean"),
            {etree.QName(self.x, "Key"): "IsExpanded"},
        )
        boolean.text = "True"
        dictionary.append(boolean)
        state.append(dictionary)
        sequence.append(state)
        [sequence.append(child) for child in children]
        return sequence

    def createBaseFile(self):
        self.__createRoot()
        self.__createTextExpression()
        self.__createMainSequence()

    def writeXmlToFile(self):
        RPA_filename = utils.utils.getFilename(self.csv_file_path).strip('_combined')
        uipath_template = os.path.join(utils.utils.MAIN_DIRECTORY, 'utils', 'UiPath_Template')
        copy_tree(uipath_template, self.UiPath_directory)
        filename = os.path.join(self.UiPath_directory, f"{RPA_filename}.xaml")
        with open(filename, "wb") as writer:
            writer.write(etree.tostring(etree.Comment('SmartRPA by marco2012 https://github.com/marco2012/smartRPA'),
                                        pretty_print=True))
            writer.write(etree.tostring(self.root, pretty_print=True))

    def __comment(self, text: str):
        self.comment += 1
        c = etree.Element(
            etree.QName(self.ui, "Comment"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Comment_{self.comment}",
                etree.QName(None, "Text"): text,
            },
        )
        self.mainSequence.append(c)

    # browser
    def __openBrowser(self, url: str = "", activities: list = None):
        openBrowser = etree.Element(
            etree.QName(self.ui, "OpenBrowser"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"OpenBrowser_1",
                etree.QName(None, "CommunicationMethod"): "{x:Null}",
                etree.QName(None, "BrowserType"): "Chrome",
                etree.QName(None, "DisplayName"): "Open Browser",
                etree.QName(None, "Hidden"): "False",
                etree.QName(None, "NewSession"): "True",
                etree.QName(None, "Private"): "False",
                etree.QName(None, "UiBrowser"): "[browserReference]",
                etree.QName(None, "Url"): url,
            },
        )
        body = etree.Element(
            etree.QName(self.ui, "OpenBrowser.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments"): "x:Object"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "x:Object",
                etree.QName(None, "Name"): "ContextTarget"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        if activities:
            activityAction.append(self.__createSequence(activities))

        body.append(activityAction)
        openBrowser.append(body)
        self.mainSequence.append(openBrowser)

    def __attachBrowser(self, activities: list):
        self.browserScope += 1
        attachBrowser = etree.Element(
            etree.QName(self.ui, "BrowserScope"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"BrowserScope_{self.browserScope}",
                etree.QName(None, "Browser"): "[browserReference]",
                etree.QName(None, "BrowserType"): "Chrome",
                etree.QName(None, "SearchScope"): "{x:Null}",
                etree.QName(None, "Selector"): "{x:Null}",
                etree.QName(None, "TimeoutMS"): "{x:Null}",
                etree.QName(None, "DisplayName"): "Attach Browser",
                etree.QName(None, "UiBrowser"): "[browserReference]",
            },
        )
        body = etree.Element(
            etree.QName(self.ui, "BrowserScope.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments"): "x:Object"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "x:Object",
                etree.QName(None, "Name"): "ContextTarget"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        activityAction.append(self.__createSequence(activities, displayName="Browser events"))
        body.append(activityAction)
        attachBrowser.append(body)
        self.mainSequence.append(attachBrowser)

    def __target(self, xpath: str = "", xpath_full: str = "", idx: str = "",
                 app: str = "", title: str = "", timeout: str = "1000"):

        selector = "{x:Null}"
        if xpath and xpath_full:
            css_selector = f"css-selector='{self.__xpathToCssSelector(xpath_full)}'"
            if len(xpath.split(')/')) == 1:
                id = f"id='{self.__getIdFromXpath(xpath)}'"
            else:
                id = f"parentid='{self.__getIdFromXpath(xpath)}'"
            if idx:
                elemIndex = f"idx='{idx}'"
            else:
                elemIndex = ""
            selector = f"<html app='chrome.exe' /><webctrl {css_selector} {id} {elemIndex}/>"
        elif app and title:
            selector = f"<wnd app='{app}' title='{title}' />"
        elif app:
            selector = f"<wnd app='{app}' />"

        props = {
            etree.QName(None, "ClippingRegion"): "{x:Null}",
            etree.QName(None, "Element"): "{x:Null}",
            etree.QName(None, "Id"): str(uuid.uuid1()),
            etree.QName(None, "Selector"): selector,
        }
        if timeout:
            props[etree.QName(None, "TimeoutMS")] = timeout

        target = etree.Element(
            etree.QName(self.ui, "Target"),
            props
        )
        target_timeout = etree.Element(
            etree.QName(self.ui, "Target.TimeoutMS"),
        )
        target_timeout.append(
            etree.Element(
                etree.QName(None, "InArgument"),
                {etree.QName(self.x, "TypeArguments"): "x:Int32"}
            )
        )
        if not timeout:
            target.append(target_timeout)
        waitForReady = etree.Element(
            etree.QName(self.ui, "Target.WaitForReady"),
        )
        waitForReady.append(
            etree.Element(
                etree.QName(None, "InArgument"),
                {etree.QName(self.x, "TypeArguments"): "ui:WaitForReady"}
            )
        )
        target.append(waitForReady)
        return target

    def __typeInto(self,
                   text: str,
                   xpath: str = "", xpath_full: str = "", idx: str = "",
                   app: str = "", title: str = "",
                   displayName: str = "Type into 'INPUT'", emptyField: bool = True,
                   timeout: str = "1000", newLine: bool = False):
        self.typeInto_id += 1
        typeInto = etree.Element(
            etree.QName(self.ui, "TypeInto"),
            {
                etree.QName(None, "AlterIfDisabled"): "{x:Null}",
                etree.QName(None, "ClickBeforeTyping"): "True",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "DelayBefore"): "{x:Null}",
                etree.QName(None, "DelayBetweenKeys"): "{x:Null}",
                etree.QName(None, "DelayMS"): "{x:Null}",
                etree.QName(None, "EmptyField"): str(emptyField),
                etree.QName(None, "SendWindowMessages"): "{x:Null}",
                etree.QName(None, "SimulateType"): "{x:Null}",
                etree.QName(None, "Activate"): "True",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"TypeInto_{self.typeInto_id}",
                etree.QName(None, "Text"): text,
            },
        )
        typeIntoTarget = etree.Element(
            etree.QName(self.ui, "TypeInto.Target"),
        )
        if xpath and xpath_full:
            target = self.__target(xpath=xpath, xpath_full=xpath_full, idx=idx, timeout=timeout)
        elif app and title:
            target = self.__target(app=app, title=title, timeout=timeout)
        else:
            target = self.__target(timeout=timeout)
        typeIntoTarget.append(target)
        typeInto.append(typeIntoTarget)
        return typeInto

    def __click(self, xpath: str, xpath_full: str, clickType="CLICK_SINGLE", mouseButton="BTN_LEFT",
                displayName: str = "Click Item"):
        self.click_id += 1
        click = etree.Element(
            etree.QName(self.ui, "Click"),
            {
                etree.QName(None, "AlterIfDisabled"): "{x:Null}",
                etree.QName(None, "DelayBefore"): "{x:Null}",
                etree.QName(None, "DelayMS"): "{x:Null}",
                etree.QName(None, "ClickType"): clickType,
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "KeyModifiers"): "None",
                etree.QName(None, "MouseButton"): mouseButton,
                etree.QName(None, "SendWindowMessages"): "{x:Null}",
                etree.QName(None, "SimulateClick"): "{x:Null}",
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Click_{self.click_id}",
            },
        )

        clickCursorPosition = etree.Element(
            etree.QName(self.ui, "Click.CursorPosition"),
        )
        cursorPosition = etree.Element(
            etree.QName(self.ui, "CursorPosition"),
            {etree.QName(None, "Position"): "Center"}
        )
        offsetx = etree.Element(
            etree.QName(self.ui, "CursorPosition.OffsetX")
        )
        offsetx.append(
            etree.Element(
                etree.QName(None, "InArgument"),
                {etree.QName(self.x, "TypeArguments"): "x:Int32"}
            )
        )
        offsety = etree.Element(
            etree.QName(self.ui, "CursorPosition.OffsetY")
        )
        offsety.append(
            etree.Element(
                etree.QName(None, "InArgument"),
                {etree.QName(self.x, "TypeArguments"): "x:Int32"}
            )
        )
        cursorPosition.extend([offsetx, offsety])
        clickCursorPosition.append(cursorPosition)

        clickTarget = etree.Element(
            etree.QName(self.ui, "Click.Target"),
        )
        clickTarget.append(self.__target(xpath, xpath_full, timeout="800"))

        click.append(clickCursorPosition)
        click.append(clickTarget)
        return click

    def __xpathToCssSelector(self, xpath: str):
        css = re.sub(r'\[([0-9]+)\]', '', xpath.lower())
        css = css.replace('/html/', '').replace('/', '>')
        return css

    def __getIdFromXpath(self, xpath: str):
        return xpath[xpath.find("(") + 1:xpath.find(")")].replace('"', '')

    def __getIdxFromXpath(self, a: str, b: str, list_index: int):
        # if list_index is 0, previous xpath is None so return empty string
        # to be comparable, xpath should have the same parent but they should not be equal,
        # otherwise difference would be 0
        if list_index > 0 and a != b and self.__getIdFromXpath(a) == self.__getIdFromXpath(b):
            # list of numbers
            aa = re.findall(r"\[\s*\+?(-?\d+)\s*\]", a)
            bb = re.findall(r"\[\s*\+?(-?\d+)\s*\]", b)
            idx = [j for i,j in zip(aa, bb) if i != j]
            try:
                return idx[0]
            except IndexError:
                return ""
        else:
            return ""

    def __navigateTo(self, url: str, displayName: str = "Navigate To"):
        self.navigateTo += 1
        navigateTo = etree.Element(
            etree.QName(self.ui, "NavigateTo"),
            {
                etree.QName(None, "Browser"): "[browserReference]",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"NavigateTo_{self.navigateTo}",
                etree.QName(None, "Url"): url,
            },
        )
        return navigateTo

    def __navigateToInNewTab(self, url: str, activities: list = None):
        return self.__openApplication(arguments=f"-new-tab {url}",
                                      fileName="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                                      selector="<wnd app='chrome.exe'/>", displayName="Navigate in New Tab",
                                      activities=activities)

    def __closeTab(self):
        self.closeTab += 1
        return etree.Element(
            etree.QName(self.ui, "CloseTab"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"CloseTab_{self.closeTab}",
                etree.QName(None, "Browser"): "{x:Null}",
                etree.QName(None, "DisplayName"): "Close tab",
            },
        )

    # excel
    def __excelSpreadsheet(self, workbookPath: str = "", password: str = "{x:Null}", attach=True,
                           displayName: str = "Excel Application Scope", activities: list = None):
        self.openApplication += 1
        if workbookPath == "":
            workbookPath = os.path.join(self.UiPath_directory, "UiPathSpreadsheet.xlsx")
        params = {
            etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelApplicationScope_{self.openApplication}",
            etree.QName(None, "Password"): password,
        }
        if attach:
            params[etree.QName(None, "ExistingWorkbook")] = "[spreadsheetReference]"
        else:
            params[etree.QName(None, "Workbook")] = "[spreadsheetReference]"
            params[etree.QName(None, "WorkbookPath")] = workbookPath

        excelApplication = etree.Element(
            etree.QName(self.ui, "ExcelApplicationScope"),
            params
        )
        body = etree.Element(
            etree.QName(self.ui, "ExcelApplicationScope.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments"): "ui:WorkbookApplication"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "ui:WorkbookApplication",
                etree.QName(None, "Name"): "ExcelWorkbookScope"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        if activities:
            activityAction.append(self.__createSequence(activities, displayName="Excel events"))

        body.append(activityAction)
        excelApplication.append(body)
        self.mainSequence.append(excelApplication)

    def __writeCell(self, cell: str, sheetName: str, text: str):
        self.writeCell += 1
        displayName = f"Write Cell {cell}"
        writeCell = etree.Element(
            etree.QName(self.ui, "ExcelWriteCell"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelWriteCell_{self.writeCell}",
                etree.QName(None, "Cell"): cell,
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "SheetName"): sheetName,
                etree.QName(None, "Text"): text,
            },
        )
        return writeCell

    def __saveWorkbook(self, displayName: str = "Save Workbook"):
        self.saveWorkbook += 1
        return etree.Element(
            etree.QName(self.ui, "ExcelSaveWorkbook"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelSaveWorkbook_{self.saveWorkbook}",
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __closeWorkbook(self, displayName: str = "Close Workbook"):
        self.closeWorkbook += 1
        return etree.Element(
            etree.QName(self.ui, "ExcelCloseWorkbook"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelSaveWorkbook_{self.closeWorkbook}",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "Workbook"): "[spreadsheetReference]",
            },
        )

    # system
    def __openApplication(self, arguments: str = "{x:Null}", fileName: str = "{x:Null}", selector: str = "{x:Null}",
                          displayName: str = "Open Application", activities: list = None):
        self.openApplication += 1
        openApplication = etree.Element(
            etree.QName(self.ui, "OpenApplication"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"OpenApplication_{self.openApplication}",
                etree.QName(None, "ApplicationWindow"): "{x:Null}",
                etree.QName(None, "TimeoutMS"): "1000",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "WorkingDirectory"): "{x:Null}",
                etree.QName(None, "Arguments"): arguments,
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "FileName"): fileName,
                etree.QName(None, "Selector"): selector,
            },
        )
        body = etree.Element(
            etree.QName(self.ui, "OpenApplication.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments"): "x:Object"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "x:Object",
                etree.QName(None, "Name"): "ContextTarget"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        if activities:
            activityAction.append(self.__createSequence(activities))

        body.append(activityAction)
        openApplication.append(body)
        return openApplication

    def __openFileFolder(self, path: str, itemName: str):
        return self.__openApplication(arguments=path,
                                      displayName=f"Open {itemName}",
                                      fileName="C:\\Windows\\explorer.exe",
                                      selector="<wnd app='explorer.exe' cls='CabinetWClass' />")

    def __closeApplication(self, app: str, title: str, displayName: str = "Start Process"):
        self.closeApplication += 1
        close = etree.Element(
            etree.QName(self.ui, "CloseApplication"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"CloseApplication_{self.closeApplication}",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "ContinueOnError"): "True",
            },

        )
        closeApplicationTarget = etree.Element(
            etree.QName(self.ui, "CloseApplication.Target"),
        )
        closeApplicationTarget.append(self.__target(app=app, title=title, timeout="1000"))
        close.append(closeApplicationTarget)
        return close

    def __startProcess(self, path: str, displayName: str = "Start Process"):
        self.startProcess += 1
        return etree.Element(
            etree.QName(self.ui, "StartProcess"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"StartProcess_{self.startProcess}",
                etree.QName(None, "Arguments"): "{x:Null}",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "FileName"): path,
                etree.QName(None, "WorkingDirectory"): "{x:Null}",
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __setToClipboard(self, text: str, displayName: str = "Set to clipboard"):
        self.setToClipboard += 1
        clipboard = etree.Element(
            etree.QName(self.ui, "SetToClipboard"),
            {
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"SetToClipboard_{self.setToClipboard}",
                etree.QName(None, "Text"): text,
            },
        )
        return clipboard

    def __sendHotkey(self, key: str = "{x:Null}", modifiers: str = "None", displayName: str = "Send Hotkey"):
        self.sendHotkey += 1
        hotkey = etree.Element(
            etree.QName(self.ui, "SendHotkey"),
            {
                etree.QName(None, "ClickBeforeTyping"): "{x:Null}",
                etree.QName(None, "DelayBefore"): "{x:Null}",
                etree.QName(None, "DelayBetweenKeys"): "{x:Null}",
                etree.QName(None, "DelayMS"): "{x:Null}",
                etree.QName(None, "EmptyField"): "{x:Null}",
                etree.QName(None, "SendWindowMessages"): "{x:Null}",
                etree.QName(None, "SpecialKey"): "{x:Null}",
                etree.QName(None, "Activate"): "True",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "Key"): key,
                etree.QName(None, "KeyModifiers"): modifiers,
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"SendHotkey_{self.sendHotkey}",
            }
        )
        sendHotkeyTarget = etree.Element(
            etree.QName(self.ui, "SendHotkey.Target"),
        )
        sendHotkeyTarget.append(self.__target())
        hotkey.append(sendHotkeyTarget)
        return hotkey

    def __createFile(self, path: str, displayName: str = "Create file"):
        self.createFile += 1
        return etree.Element(
            etree.QName(self.ui, "CreateFile"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"CreateFile_{self.createFile}",
                etree.QName(None, "ContinueOnError"): "{x:Null}",
                etree.QName(None, "Name"): "{x:Null}",
                etree.QName(None, "Path"): path,
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __createDirectory(self, path: str, displayName: str = "Create file"):
        self.createDirectory += 1
        return etree.Element(
            etree.QName(self.ui, "CreateDirectory"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"CreateDirectory_{self.createDirectory}",
                etree.QName(None, "ContinueOnError"): "{x:Null}",
                etree.QName(None, "Path"): path,
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __moveFile(self, from_path: str, to_path: str, displayName: str = "Move file"):
        self.moveFile += 1
        return etree.Element(
            etree.QName(self.ui, "MoveFile"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"MoveFile_{self.moveFile}",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "Destination"): to_path,
                etree.QName(None, "Overwrite"): "True",
                etree.QName(None, "Path"): from_path,
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __delete(self, path: str, displayName: str = "Move file"):
        self.moveFile += 1
        return etree.Element(
            etree.QName(self.ui, "Delete"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Delete_{self.moveFile}",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "Path"): path,
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    # powerpoint
    def __powerpointScope(self, num_slides: int, path: str = "", displayName: str = "PowerPoint Presentation"):
        self.powerpointApplicationCard += 1
        position = self.powerpointApplicationCard
        if not path:
            path = os.path.join(self.UiPath_directory, "presentation.xlsx")
        powerpointApplication = etree.Element(
            etree.QName(self.upadb, "PowerPointApplicationCard"),
            {
                etree.QName(self.sap2010,
                            "WorkflowViewState.IdRef"): f"PowerPointApplicationCard_{self.powerpointApplicationCard}",
                etree.QName(None, "Password"): "{x:Null}",
                etree.QName(None, "CreateIfNotExists"): "True",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "PresentationPath"): path,
            }
        )
        body = etree.Element(
            etree.QName(self.upadb, "PowerPointApplicationCard.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments"): "ui:IPresentationQuickHandle"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "ui:IPresentationQuickHandle",
                etree.QName(None, "Name"): "powerpointReference"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        slides = [self.__insertSlide(position) for position in range(1, num_slides + 1)]
        activityAction.append(self.__createSequence(slides, displayName="Powerpoint events"))

        body.append(activityAction)
        powerpointApplication.append(body)
        self.mainSequence.append(powerpointApplication)

    def __insertSlide(self, position):
        self.insertSlide += 1
        return etree.Element(
            etree.QName(self.upab, "InsertSlideX"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"InsertSlideX_{self.insertSlide}",
                etree.QName(None, "LayoutName"): "{x:Null}",
                etree.QName(None, "SlideMasterName"): "{x:Null}",
                etree.QName(None, "DisplayName"): "Insert Slide",
                etree.QName(None, "InsertPosition"): str(position),
                etree.QName(None, "Presentation"): "[powerpointReference]",
            },
        )

    # generate RPA
    def __generateRPA(self, df: pandas.DataFrame):
        # check if dataframe contains values
        if df.empty:
            return False

        self.__comment("// Generated using SmartRPA available at "
                       "https://github.com/bpm-diag/smartRPA")

        # if dataframe contains browser related events add openBrowser element
        if not df.query('category=="Browser"').empty:
            url = df.loc[df['category'] == 'Browser', 'browser_url'].iloc[0]
            self.__openBrowser(url=url)

        # if dataframe contains excel events, add excel scope element
        v = df['concept:name'].values
        if 'newWorkbook' in v:
            self.__excelSpreadsheet(workbookPath="", attach=False)
        if 'openWorkbook' in v:
            wb_path = df.loc[df['concept:name'] == 'openWorkbook', 'event_src_path'].iloc[0]
            os_user = df['org:resource'].iloc[0]
            path = utils.utils.convertToWindowsPath(wb_path, os_user)
            self.__excelSpreadsheet(workbookPath=path, attach=False)

        browserActivities = []
        excelActivities = []
        systemActivities = []
        previousCategory = df.loc[0, 'category']
        ppt_slides_inserted = False

        for index, row in df.iterrows():
            ######
            # Variables
            ######
            try:
                e = row['event_type']
                timestamp = row['timestamp']
                user = row['user']
            except KeyError:
                e = row['concept:name']
                timestamp = row['time:timestamp']
                user = row['org:resource']

            wb = row['workbook']
            sh = row['current_worksheet']
            cell_value = utils.utils.unicodeString(row['cell_content'])
            cell_range = row['cell_range']
            range_number = row['cell_range_number']
            app = row['application']
            cb = utils.utils.processClipboard(row['clipboard_content'])
            path = ""
            item_name = ""
            currentCategory = row["category"]
            if not pandas.isna(row['event_src_path']) \
                    and row['event_src_path'] != '' \
                    and '.tmp' not in row['event_src_path']:
                path = row['event_src_path']
                path = utils.utils.convertToWindowsPath(path, user)
                item_name = path.replace('\\', r'\\')
            dest_path = ""
            if not pandas.isna(row['event_dest_path']) \
                    and row['event_dest_path'] != ''\
                    and '.tmp' not in row['event_dest_path']:
                dest_path = row['event_dest_path']
                dest_path = utils.utils.convertToWindowsPath(
                    dest_path, user)
            url = "about:blank"
            if not pandas.isna(row['browser_url']):
                url = row['browser_url']
            id = ""
            if not pandas.isna(row['id']):
                id = row['id']
            xpath = row['xpath']
            xpath_full = row['xpath_full']
            value = utils.utils.unicodeString(row['tag_value'])

            if e in ["logonComplete"]:
                continue

            ######
            # Check sequence
            ######
            # print(f"[DEBUG] {index}) Event={e} PreviousCat={previousCategory}, CurrentCat={currentCategory}")
            # OperatingSystem and Clipboard should be in the same sequence
            if (previousCategory != currentCategory) \
                    and not ((previousCategory == 'OperatingSystem' and currentCategory == 'Clipboard') or
                             (previousCategory == 'Clipboard' and currentCategory == 'OperatingSystem')):
                previousCategory = currentCategory
                if browserActivities:
                    self.__attachBrowser(activities=browserActivities)
                    browserActivities.clear()
                if excelActivities:
                    self.__excelSpreadsheet(activities=excelActivities)
                    excelActivities.clear()
                if systemActivities:
                    self.mainSequence.append(self.__createSequence(systemActivities, displayName="System events"))
                    systemActivities.clear()

            ######
            # Browser
            ######
            if e == "newTab" and int(id) != 0:
                # browserActivities.append(self.__navigateToInNewTab(""))
                self.__comment("new tab event not supported by UiPath")
                continue
            if e == "selectTab":
                # browserActivities.append(self.__sendHotkey(id, "Ctrl", f"Select tab {id}"))
                continue
            if e == "closeTab":
                # browserActivities.append(self.__closeTab())
                continue
            if (e in ["clickLink", "typed", "reload", "link"]) and not (any([x in url for x in ['chrome-extension', 'chrome-search://']])):
                browserActivities.append(self.__navigateTo(url))
            if e == "mouseClick" or e == "clickButton" or e == "clickRadioButton" or e == "clickCheckboxButton":
                browserActivities.append(
                    self.__click(xpath, xpath_full, displayName=f"Clicking {row['tag_category'].lower()}"))
            if e == "doubleClick" and xpath != '':
                browserActivities.append(self.__click(xpath, xpath_full, clickType="CLICK_DOUBLE"))
            if e == "changeField":
                if row['tag_category'] == "SELECT":
                    continue
                else:
                    # list of all xpaths in the dataframe having changeField as concept name
                    # so the user inserted text in an input
                    list_of_xpaths = df.loc[df['concept:name'] == 'changeField']['xpath'].tolist()
                    # current xpath
                    b = xpath
                    # index of current xpath
                    list_index = list_of_xpaths.index(b)
                    # previous xpath
                    a = list_of_xpaths[list_index - 1]
                    # compare current xpath to previous one to find differences
                    # pass index of current xpath because if it's 0, previous is None so idx is empty
                    idx = self.__getIdxFromXpath(a, b, list_index)
                    browserActivities.append(self.__typeInto(text=value, xpath=xpath, xpath_full=xpath_full, idx=idx, timeout="2000"))

            ######
            # Excel
            ######
            if e in ["addWorksheet", "WorksheetAdded"]:
                excelActivities.append(self.__writeCell(cell="", sheetName=sh, text=""))
            if e in ["selectWorksheet", "WorksheetActivated"]:
                continue
            if e == "getCell":
                continue
            if e in ["editCellSheet", "editCell", "editRange"]:
                excelActivities.append(self.__writeCell(cell=cell_range, sheetName=sh, text=cell_value))
            if e == "getRange":
                continue
            if e == "saveWorkbook":
                excelActivities.append(self.__saveWorkbook(displayName=f"Save {wb}"))
            if e == "printWorkbook":
                continue
            if e == "closeWindow":
                excelActivities.append(self.__closeWorkbook(displayName=f"Close {wb}"))

            ######
            # System
            ######
            if (e == "copy" or e == "cut") and not pandas.isna(cb):
                systemActivities.append(self.__setToClipboard(cb))
            if e == "paste" and row['category'] != 'Browser' and app != 'Excel':
                systemActivities.append(
                    self.__typeInto(text=cb, app=app+'*', title=row["title"],
                                    displayName=f"Paste into {row['title']}", emptyField=False, newLine=True))
            if e == "pressHotkey":
                hotkey = row["id"]
                modifiers = ', '.join(list(map(lambda x: string.capwords(x), hotkey.split('+')[:-1])))
                systemActivities.append(self.__sendHotkey(key=hotkey[-1], modifiers=modifiers,
                                                          displayName=f"Press {hotkey.upper()} - {row['description']}"))
            if e in ["openFile", "openFolder"] and path:
                systemActivities.append(self.__openFileFolder(path, item_name))
            if e == "programOpen":
                # don't open excel or powerpoint if there are events related to them in dataframe because it is already handled
                try:
                    event_list = df['event_type'].tolist()
                except KeyError:
                    event_list = df['concept:name'].tolist()
                if (app in ["EXCEL.EXE", "Microsoft Excel", "Microsoft Excel (MacOS)", "Microsoft Powerpoint", "POWERPNT.EXE"]) and any(
                        i in event_list for i in ["newWorkbook", "selectWorksheet", "WorksheetActivated", "newPresentation"]):
                    continue
                if path and ntpath.basename(path) not in modules.events.systemEvents.programs_to_ignore:
                    systemActivities.append(self.__startProcess(path, displayName=f"Open {app}"))
            if e == "programClose" and app not in modules.events.systemEvents.programs_to_ignore:
                title = row['title']
                displayName = f"Close {title}" if title else f"Close {app}"
                systemActivities.append(self.__closeApplication(app=app + '*', title=row["title"], displayName=displayName))

            if e == "created" and path:
                if os.path.splitext(path)[1]:  # file
                    systemActivities.append(self.__createFile(path, displayName=f"Create {item_name}"))
                else:  # directory
                    systemActivities.append(self.__createDirectory(path, displayName=f"Create {item_name}"))
            if e in ["moved", "Unmount"] and path:
                new_name = utils.utils.unicodeString(ntpath.basename(dest_path))
                if os.path.dirname(path) == os.path.dirname(dest_path):
                    displayName = f"Rename file as {new_name}"
                else:
                    displayName = f"Move file to {new_name}"
                systemActivities.append(self.__moveFile(path, dest_path, displayName))
            if e == "deleted" and path:
                systemActivities.append(self.__delete(path, displayName=f"Delete {item_name}"))

            # word
            if e == "newDocument":
                systemActivities.append(
                    self.__startProcess(r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.exe",
                                        displayName="Open Word"))
            if e == "saveDocument":
                continue

            # powerpoint
            if e == "newPresentation":
                # presPath = path if path else ""
                # self.__powerpointScope(path=presPath, insertSlide=False)
                continue
            if e == "newPresentationSlide" and not ppt_slides_inserted:
                ppt_slides_inserted = True
                presPath = path if path else ""
                num_slides = len(df[df['concept:name'] == 'newPresentationSlide'])
                self.__powerpointScope(num_slides, path=presPath)
            if e == "savePresentation":
                continue
            if e == "closePresentation":
                continue

        if browserActivities:
            self.__attachBrowser(activities=browserActivities)
            browserActivities.clear()
        if excelActivities:
            self.__excelSpreadsheet(activities=excelActivities)
            excelActivities.clear()
        if systemActivities:
            self.mainSequence.append(self.__createSequence(systemActivities, displayName="System events"))
            systemActivities.clear()

        self.status_queue.put(f"[UiPath] Generated UiPath RPA script")

    def generateUiPathRPA(self, df: pandas.DataFrame):
        self.createBaseFile()
        self.__generateRPA(df)
        self.writeXmlToFile()

    def test(self):
        self.createBaseFile()
        presPath = r"C:\Users\marco\Desktop\pres.pptx"
        self.__powerpointScope(path=presPath, insertSlide=False)
        self.__powerpointScope(path=presPath, insertSlide=True)
        filename = r"/Users/marco/Desktop/RPA/ppt.xaml"
        with open(filename, "wb") as writer:
            writer.write(etree.tostring(self.root, pretty_print=True))

