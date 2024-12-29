-- Max Reed
-- December 28, 2024
-- This script writes out all system, by number and including any assignment, together with all spins associated with that system (with labels).

-- Script to count spin systems in a project

-- Version 1: 2.March 2006 F. Damberger
-- modified to introduce user dialog window which remembers values

-- ----------------------------------------------------------------------
-- Create array to hold all script variables
t={}

-- User can edit parameters below to adapt to the project:
-- ----------------------------------------------------------------------
-- ======================== Define functions ============================

-- ----------------------------------------------------------------------

-- ----------------------------------------------------------------------

-- ====================== Get Selections from User ======================

--1. Set up dialog window
v = gui.createMainWindow()
v:setCaption( "RemoveSelectedSystems dialog" )
t.frm = gui.createGrid( v, 2, false )
v:setCentralWidget( t.frm )
v:show()
t.frm:show()

-- Labels for first two columns
t.ProjectListLabel = gui.createLabel( t.frm, "Select Project" )
t.ProjectListCB = gui.createComboBox( t.frm )


--2. Read ProjectNames into ProjectList combobox

SelectedItemIndex = nil
for Id,Project in pairs( cara:getProjects() ) do
	ItemIndex = t.ProjectListCB:addItem( Project:getName() )
	t.ProjectListCB:setCurrentItem( ItemIndex )
	if CountSystemsProjectName == t.ProjectListCB:getCurrentText() then
		SelectedItemIndex = ItemIndex
	end
end -- for all projects

if SelectedItemIndex then -- set to previous choice if it exists
	t.ProjectListCB:setCurrentItem( SelectedItemIndex )
end

-- Display ProjectList Combobox
t.ProjectListLabel:show()
t.ProjectListCB:show()

--3. ResidueRange 


-- Checkboxes follow ------------------------------------------


-- ----------------------------------------------------------------------

--5. Checkbox Ignore ResidueAssignments

t.IgnoreResidues_ChBxLabel = gui.createLabel( t.frm, "Ignore residue assignments (remove system numbers): " )
t.IgnoreResidues_ChBx = gui.createCheckBox( t.frm )

if CountSystemsIgnoreResidues == true then -- determine if Selection was made previously
	t.IgnoreResidues_ChBx:setChecked()
end
t.IgnoreResidues_ChBxLabel:show()
t.IgnoreResidues_ChBx:show()

--6. OK and Cancel Buttons

t.okbutton = gui.createPushButton(t.frm, "OK" )
t.cancelbutton = gui.createPushButton( t.frm, "Cancel" )

t.okbutton:show()
t.cancelbutton:show()

-- ============ Callbacks for menu window ===============================

-- Define Callbacks for the buttons


-- cancel button Callback
t.cancelbutton:setCallback( gui.event.Clicked,
	function (self)
		v:close()
	end
)

-- OK button Callback
t.okbutton:setCallback( gui.event.Clicked,
	function (self)
-- =============== Determine User Preferences ===========================
		t.P = cara:getProject( t.ProjectListCB:getCurrentText() )
		CountSystemsProjectName = t.P:getName()

-- =============== Count Residues ================================
		NumSys = 0
		-- get Sequence
		t.Seq = t.P:getSequence()
			-- get Systems			
		t.Sys = t.P:getSystems()
					
		-- loop through the Systems
		for a,b in pairs( t.Sys ) do
			print("System\t"..a)
			NumSys = NumSys + 1
			t.Spins = b:getSpins()
			t.Residue = b:getResidue()
			if t.Residue then
				t.ResNum = t.Residue:getId()
				print("Res Num\t"..t.ResNum)
			else
				print("No Assignment\t-1")
			end
			for c,d in pairs( t.Spins ) do
				t.Label = d:getLabel()
				t.SpinVal = d:getShift()
				print(t.Label.."\t"..t.SpinVal)
			end -- for all spins in system
			print("")
		end
		v:close()
	end
)


-- t = {}