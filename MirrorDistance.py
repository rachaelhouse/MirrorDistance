import os
import unittest
import vtk, qt, ctk, slicer
import math
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
#
# MirrorDistance
#

class MirrorDistance(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "MirrorDistance" # TODO make this more human readable by adding spaces
    self.parent.categories = ["SurfaceDistances"]
    self.parent.dependencies = []
    self.parent.contributors = ["Rachael House (Perklab, Queen's University)"] #
    self.parent.helpText = """
    
    """
    self.parent.acknowledgementText = """
   
""" # replace with organization, grant and thanks.

#
# MirrorDistanceWidget
#

class MirrorDistanceWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
    #input model slector

    self.inputModelSelector = slicer.qMRMLNodeComboBox()
    self.inputModelSelector.nodeTypes = [ "vtkMRMLModelNode" ]
    self.inputModelSelector.selectNodeUponCreation = True
    self.inputModelSelector.addEnabled = False
    self.inputModelSelector.removeEnabled = False
    self.inputModelSelector.noneEnabled = False
    self.inputModelSelector.showHidden = False
    self.inputModelSelector.showChildNodeTypes = False
    self.inputModelSelector.setMRMLScene( slicer.mrmlScene )
    self.inputModelSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Model: ", self.inputModelSelector)

    # input model slector
    #optional input selector for seperate scan instead od same scan
    self.inputModelSelector2 = slicer.qMRMLNodeComboBox()
    self.inputModelSelector2.nodeTypes = ["vtkMRMLModelNode"]
    self.inputModelSelector2.selectNodeUponCreation = True
    self.inputModelSelector2.addEnabled = False
    self.inputModelSelector2.removeEnabled = False
    self.inputModelSelector2.noneEnabled = True
    self.inputModelSelector2.showHidden = False
    self.inputModelSelector2.showChildNodeTypes = False
    self.inputModelSelector2.setMRMLScene(slicer.mrmlScene)
    self.inputModelSelector2.setToolTip("Pick the input to the algorithm.")
    parametersFormLayout.addRow("Input Model (Optional): ", self.inputModelSelector2)

    # input Fiducal slector
    self.inputFiducialSelector = slicer.qSlicerSimpleMarkupsWidget()
    self.inputFiducialSelector.tableWidget().hide()
    self.inputFiducialSelector.setMRMLScene(slicer.mrmlScene)
    self.inputFiducialSelector.setToolTip("Pick the fiducials to define the region of interest.")
    self.inputFiducialSelector.setNodeBaseName("Input Fiducials for ROI")
    parametersFormLayout.addRow("Input fiducials: ", self.inputFiducialSelector)
    # Enable place multiple marukps by default
    placeWidget = self.inputFiducialSelector.markupsPlaceWidget()
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    placeWidget.placeModeEnabled = False
    placeWidget.placeModeEnabled = True



    self.transformSelector = slicer.qMRMLNodeComboBox()
    self.transformSelector.nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
    self.transformSelector.selectNodeUponCreation = True
    self.transformSelector.addEnabled = True
    self.transformSelector.removeEnabled = True
    self.transformSelector.noneEnabled = True
    self.transformSelector.showHidden = False
    self.transformSelector.showChildNodeTypes = False
    self.transformSelector.renameEnabled = True
    self.transformSelector.setMRMLScene( slicer.mrmlScene )
    self.transformSelector.setToolTip( "Pick the moving to fixed transform computed by the algorithm." )
    parametersFormLayout.addRow("Initial Transform (Optional): ", self.transformSelector)

    #output Model selector
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.outputSelector.selectNodeUponCreation = False
    self.outputSelector.addEnabled = True
    self.outputSelector.renameEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.baseName = "Model"
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Model: ", self.outputSelector)

    # Apply Button
    self.ApplyButton = qt.QPushButton("Apply")
    self.ApplyButton.enabled = True
    parametersFormLayout.addRow("", self.ApplyButton)

    # connections
    self.ApplyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.inputModelSelector2.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.inputFiducialSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.transformSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    self.distanceLabel = qt.QLabel()
    self.distanceLabel.setText("Mean distance after registration")
    parametersFormLayout.addRow("Average Scalar Value: ", self.distanceLabel)


    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.ApplyButton.enabled = self.inputModelSelector.currentNode()
    self.ApplyButton.enabled = self.inputModelSelector2.currentNode()
    self.ApplyButton.enabled = self.outputSelector.currentNode()
    self.ApplyButton.enabled = self.inputFiducialSelector.currentNode()

  def onApplyButton(self):
    logic = MirrorDistanceLogic()
    logic.run(self.inputModelSelector.currentNode(),self.outputSelector.currentNode(), self.transformSelector.currentNode(), self.distanceLabel, self.inputModelSelector2.currentNode(), self.inputFiducialSelector.currentNode())


class MirrorDistanceLogic(ScriptedLoadableModuleLogic):

  def FiducialsToPolyData(self, fiducials, polyData):
    # create polydata from fiducial list
    points = vtk.vtkPoints()
    n = fiducials.GetNumberOfFiducials()
    for fiducialIndex in range(0, n):
      p = [0, 0, 0]
      fiducials.GetNthFiducialPosition(fiducialIndex, p)
      points.InsertNextPoint(p)
    tempPolyData = vtk.vtkPolyData()
    tempPolyData.SetPoints(points)

    vertex = vtk.vtkVertexGlyphFilter()
    vertex.SetInputData(tempPolyData)
    vertex.Update()

    polyData.ShallowCopy(vertex.GetOutput())

  def MirrorInput(self, inputModel, outputModel, initialTransform, distance, inputModel2, fids):
    #Mirror Input Model
    if inputModel2 == None:
      surfaceMirrored = inputModel.GetPolyDataConnection()
      mirrorTransformMatrix = vtk.vtkMatrix4x4()
      mirrorTransformMatrix.SetElement(0, 0, -1)
      mirrorTransform = vtk.vtkTransform()
      mirrorTransform.SetMatrix(mirrorTransformMatrix)
      transformFilter = vtk.vtkTransformPolyDataFilter()
      transformFilter.SetInputConnection(surfaceMirrored)
      transformFilter.SetTransform(mirrorTransform)
      transformFilter.Update()
      surfaceMirrored = transformFilter.GetOutputPort()
      if mirrorTransformMatrix.Determinant() < 0:
        reverse = vtk.vtkReverseSense()
        reverse.SetInputConnection(surfaceMirrored)
        surfaceMirrored = reverse.GetOutputPort()
    else:
        surfaceMirrored = inputModel2.GetPolyData()

    #SurfaceMirrored now stores the mirrored input
    surface = inputModel.GetPolyData()
    #run ICP between surface and Mirrored Surface 
    modelsLogic = slicer.modules.models.logic()
    OutputModel = modelsLogic.AddModel(surfaceMirrored) 
    OutputModel.GetDisplayNode().SetVisibility(False)
    OutputModel.SetName("MirroredInput")
    OutputModel.GetDisplayNode().BackfaceCullingOff()

    #use initial transform when the icp algorithm gets stuck in a local minimum
    if initialTransform != None:
        OutputModel.SetAndObserveTransformNodeID(initialTransform.GetID())
        transformLogic = slicer.vtkSlicerTransformLogic()
        transformLogic.hardenTransform(OutputModel)

    #Register Mirror and Input Model using ICP 
    icpTransform = vtk.vtkIterativeClosestPointTransform()
    icpTransform.SetSource(inputModel.GetPolyData())
    icpTransform.SetTarget(OutputModel.GetPolyData())
    icpTransform.GetLandmarkTransform().SetModeToRigidBody()
    icpTransform.SetMaximumNumberOfIterations(100)
    icpTransform.Inverse()
    icpTransform.Modified()
    icpTransform.Update()

    #Aply the ICP transform
    icpMatrixTransform = vtk.vtkTransform()
    icpMatrixTransform.SetMatrix(icpTransform.GetMatrix())
    transformFilterICP = vtk.vtkTransformPolyDataFilter()
    transformFilterICP.SetInputConnection(OutputModel.GetPolyDataConnection())
    transformFilterICP.SetTransform(icpMatrixTransform)
    transformFilterICP.Update()
    surfaceRegMirrored = transformFilterICP.GetOutput()


    modelsLogic = slicer.modules.models.logic()
    mirroredModel = modelsLogic.AddModel(surfaceRegMirrored) 
    mirroredModel.GetDisplayNode().SetVisibility(False)
    mirroredModel.SetName("MirroredRegisteredInput")
    mirroredModel.GetDisplayNode().BackfaceCullingOff()

    #clean the CLI Model to Model distance model using the orginal surface and the mirrored registered surface as input
    # store module output in output model provided 
    params = {'vtkFile1': inputModel.GetID(), 'vtkFile2': mirroredModel.GetID()  , 'vtkOutput' : outputModel.GetID(), 'distanceType' : 'signed_closest_point', 'targetInFields' : False}
    cliNode = slicer.cli.runSync(slicer.modules.modeltomodeldistance, None, params)

    # Crop the inputmodels to the region of interest
    ROI = vtk.vtkPolyData()
    self.FiducialsToPolyData(fids, ROI)
    maxRad = 0
    CenterOfMass = vtk.vtkCenterOfMass()
    CenterOfMass.SetInputData(ROI)
    CenterOfMass.SetUseScalarsAsWeights(False)
    CenterOfMass.Update()
    center = CenterOfMass.GetCenter()

    for i in range(ROI.GetNumberOfPoints()):
      point = ROI.GetPoint(i)
      dis = abs(vtk.vtkMath().Distance2BetweenPoints(center, point))
      if dis > maxRad:
        maxRad = dis

    sphere = vtk.vtkSphere()
    sphere.SetCenter(center)
    sphere.SetRadius(math.sqrt(maxRad))

    clippedOutput = vtk.vtkClipPolyData()
    clippedOutput.SetClipFunction(sphere)  # should be loop
    clippedOutput.SetInputData(outputModel.GetPolyData())
    clippedOutput.SetInsideOut(True)
    clippedOutput.Update()

    #cropped output, comment to have whole model distance
    outputModel.SetAndObservePolyData(clippedOutput.GetOutput())

    inputModel.GetDisplayNode().SetVisibility(False)
    outputModel.GetDisplayNode().SetVisibility(True)
    #It is recommended to change the Color Table under Scalars to: ColdtoHotRainbow
    outputModel.GetDisplayNode().SetActiveScalarName("Signed")


  def ComputeMeanDistance(self, inputSourceModel, inputTargetModel, transform ):
    sourcePolyData = inputSourceModel#.GetPolyData()
    targetPolyData = inputTargetModel.GetPolyData()

    cellId = vtk.mutable(0)
    subId = vtk.mutable(0)
    dist2 = vtk.mutable(0.0)
    locator = vtk.vtkCellLocator()
    locator.SetDataSet( targetPolyData )
    locator.SetNumberOfCellsPerBucket( 1 )
    locator.BuildLocator()
    
    totalDistance = 0.0

    sourcePoints = sourcePolyData.GetPoints()
    n = sourcePoints.GetNumberOfPoints()
    m = vtk.vtkMath()
    for sourcePointIndex in xrange(n):
      sourcePointPos = [0, 0, 0]
      sourcePoints.GetPoint( sourcePointIndex, sourcePointPos )
      transformedSourcePointPos = [0, 0, 0, 1]
      sourcePointPos.append(1)
      transform.MultiplyPoint( sourcePointPos, transformedSourcePointPos )  
      surfacePoint = [0, 0, 0]
      transformedSourcePointPos.pop()
      locator.FindClosestPoint( transformedSourcePointPos, surfacePoint, cellId, subId, dist2 )
      totalDistance = totalDistance + math.sqrt(dist2)

    return ( totalDistance / n )

  def run(self, inputModel, outputModel, initialTransform, distance, inputModel2, fids):

    self.MirrorInput(inputModel, outputModel, initialTransform, distance, inputModel2, fids)
    return True
    
    logging.info('Processing completed')



class MirrorDistanceTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_MirrorDistance1()

  def test_MirrorDistance1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    self.delayDisplay('Test passed!')
